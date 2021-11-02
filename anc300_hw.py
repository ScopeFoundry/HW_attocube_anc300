from ScopeFoundry.logged_quantity import LoggedQuantity
from ScopeFoundryHW.attocube_anc300.anc300_device import AttocubeANC300Piezo
from ScopeFoundry import HardwareComponent


class AttocubeANC300StageHW(HardwareComponent):

    name = 'attocube_anc300'

    def __init__(self, app, debug=False, name=None, ax_names='xy'):
        self.ax_names = ax_names
        HardwareComponent.__init__(self, app, debug=debug, name=name)


    def setup(self):

        #set the piezo specifications for voltage and max translation
        self.max_volt=60 #max voltage on the piezo stages in V
        self.max_move=40 #max translation the piezo stages can make in um

        self.settings.New('port', dtype=str, initial='COM11')


        for axis in self.ax_names:
            # Skip axis if disable in __init__ ax_names
            if axis == '_':
                continue

            self.settings.New(axis + "_mode", dtype=str, choices = AttocubeANC300Piezo.modes )
            
            pos = self.settings.New(axis + "_position", 
                               dtype=float,
                               ro=True,
                               unit='um',
                               spinbox_decimals=6,
                               si=False
                               )

            raw = self.settings.New(axis + "_raw", 
                               dtype=float,
                               ro=True,
                               unit='V',
                               spinbox_decimals=6,
                               si=False
                               )

            LoggedQuantity                           
            
            #self.settings.New(axis + "_ref_position", dtype=float, ro=True, unit='nm')
            
            self.settings.New(axis + "_target_position",
                                dtype=float,
                                ro=False,
                                vmin=0,
                                vmax=self.max_move,
                                unit='um',
                                spinbox_decimals=6,
                                spinbox_step=0.01,
                                si=False)
            
            calib = self.settings.New( axis + "_calib", dtype=float, ro=False, initial=self.max_move/self.max_volt, unit='um/V')

            self.settings.New(axis + "_jog_step", dtype=float,
                            spinbox_decimals=6, si = False, unit='um', ro=False,
                            initial=1)

            if axis=='x':
                pos.connect_lq_math( (raw, calib), lambda raw,calib: raw*calib)
            elif axis=='y':
                #this effectively switches the direction of the y axis to account for the 90deg twist of that the stage is apprently mounted at
                pos.connect_lq_math( (raw, calib), lambda raw,calib: abs(raw-self.max_volt)*calib)

            for sign in "pm":
                # Seems that pyqt passes a bool to func if func has arguments. ?
                # dump bool into *args and ignore
                func = lambda *args, axis=axis, sign=sign: self.move_jog_step(
                        axis=axis, sign=sign)     
                self.add_operation(axis + "_jog_"+sign, func)    

    def connect(self):
        if self.settings['debug_mode']: print("connecting to attocube ANC300 {}".format(self.name))
        
        S = self.settings
        self.anc = anc = AttocubeANC300Piezo(port=S['port'], debug=S['debug_mode'])
        for axis_num, axis_name in [(1,self.ax_names[0]),(0,self.ax_names[1])]: # y and z positioners are switched on the hardware side (they are x=1, y=0). It seems the Stage is mounted at a 90deg angle. Here we switch them back by adjusting the numbering
            
            axis_num += 1
            print(axis_num, axis_name)
            if axis_name != "_":
                
                # connect logged quantities

                self.settings.get_lq(axis_name + "_mode").connect_to_hardware(
                    read_func = lambda a=axis_num: self.anc.get_mode(a),
                    write_func = lambda m, a=axis_num: self.anc.set_mode(a, m))

                
                raw = self.settings.get_lq(axis_name + "_raw")
                raw.connect_to_hardware(
                    lambda a=axis_num: self.anc.get_offset_volt(a))

                raw.read_from_hardware()

                target = self.settings.get_lq(axis_name + "_target_position")
                target.update_value(self.settings[axis_name + "_position"])

                def set_target_pos(new_pos, axis_num=axis_num, axis_name=axis_name):
                    if axis_name=='x':
                        new_volt = new_pos / self.settings[axis_name + "_calib"]
                    elif axis_name=='y':
                        #again switching the y axis direction here (this is the reverse function of the calibration top)
                        new_volt = abs(new_pos-self.max_move) / self.settings[axis_name + "_calib"]

                    self.anc.set_offset_volt(axis_num, new_volt)
                    self.settings.get_lq(axis_name + "_raw").read_from_hardware()

                target.connect_to_hardware(
                    write_func = set_target_pos)




    

    def disconnect(self):
        self.settings.disconnect_all_from_hardware()
        
        if hasattr(self, 'anc'):
            self.anc.close()
            
            del self.anc

    def move_jog_step(self, axis_name, sign):
        S = self.settings
        delta = {"p": 1.0, "m": -1.0}[sign] * S[axis_name + "_jog_step"]
        newpos=S[axis_name + "_target_position"] + delta
        if newpos>=self.max_move:
            S[axis_name + "_target_position"]=self.max_move
        elif newpos<=0:
            S[axis_name + "_target_position"]=0
        else:
            S[axis_name + "_target_position"]=newpos
