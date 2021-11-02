import serial
import logging


logger = logging.getLogger(__name__)


class AttocubeANC300Piezo(object):

    def __init__(self, port, debug=False):

        self.port = port
        self.debug = debug
        
        if self.debug: logger.debug( "FlipMirrorArduino init, port=%s" % self.port )
        
        self.ser = serial.Serial(port=self.port, baudrate=38400, timeout=0.100)
        
    def close(self):
        self.ser.close()

    def ask(self, cmd):
        self.ser.write( cmd.encode() + b'\r\n')
        line = ""
        resp = []
        while line != ">":
            line = self.ser.readline().decode().strip()
            resp.append(line)
           # print("-->", line)

        assert resp[0] == cmd

        if resp[-2] != 'OK':
            #print('error!')
            raise IOError("AttocubeANC300Piezo Command Failed: " + cmd + " --> " + str(resp))

        return resp[1:-2]

    def get_version(self):
        resp = self.ask('ver')
        return ' '.join(resp)

    def get_offset_volt(self, axis):
        resp = self.ask(f'geta {axis:d}')
        # example: resp = ['voltage = 0.000000 V']
        # resp[0].split --> ['voltage', '=', '0.000000', 'V']

        resp = resp[0].split()[2]
        
        resp = float(resp)

        return resp


    def set_offset_volt(self, axis, volt):
        cmd = f"seta {axis:d} {volt:0.6f}"
        resp = self.ask(cmd)
        return resp

    def get_mode(self, axis):
        cmd = f"getm {axis:d}"
        resp = self.ask(cmd)
        # ['mode = gnd']
        resp = resp[0].split()[-1]
        return resp

    modes = [
        'gnd', # gnd: Setting to this mode diables all outputs and connects them to chassis mass.
        'inp', # inp: In this mode, AC-IN and DC-IN can be enabled using the setaci and setdci commands. Setting to inp mode disables stepping and offset modes.
        'cap', # cap: Setting to cap mode starts a capacitance measurement. The axis returns to gnd mode afterwards. It is not needed to switch to gnd mode before.
        'stp', # stp: This enables stepping mode. AC-IN and DC-IN functionalities are not modified, while an offset function would be turned off.
        'off', # off: This enables offset mode. AC-IN and DC-IN functionalities are not modified, while any stepping would be turned off.
        'stp+',# stp+: This enables additive offset + stepping mode. Stepping wave- forms are added to an offset. AC-IN and DC-IN functionalities are not modified.
        'stp-',#stp-: This enables subtractive offset + stepping mode. Stepping waveforms are subtracted from an offset. AC-IN and DC-IN function- alities are not modified.        
        ]

    def set_mode(self, axis, mode):
        assert mode in self.modes
        cmd = f"setm {axis:d} {mode}"
        resp = self.ask(cmd)
        return resp


if __name__ == '__main__':

    a = AttocubeANC300Piezo(port='COM11', debug=True)

    a.ask('ver')
    a.ask('ver')
    a.ask('ver')
    print(a.ask('ver'))

    print(a.get_version())
    print(a.set_mode(1, 'off'))
    print(a.set_mode(2, 'off'))
    print(a.get_mode(1))

    print(a.get_offset_volt(1))
    print(a.set_offset_volt(2, 5))
    print(a.get_offset_volt(1))

    a.close()