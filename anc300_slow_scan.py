from ScopeFoundry.scanning import BaseRaster2DSlowScan

class AttocubeANC300_2DSlowScan(BaseRaster2DSlowScan):

    name = 'anc300_raster'
    
    def __init__(self, app, hw_name="attocube_anc300"):
        self.hw_name = hw_name
        BaseRaster2DSlowScan.__init__(self, app,
                                      h_limits=(0,50), v_limits=(0,50),
                                      h_spinbox_step = 0.100, v_spinbox_step=0.10,
                                      h_unit="um", v_unit="um",circ_roi_size=1.0)


    def setup(self):
        BaseRaster2DSlowScan.setup(self)
        self.stage = self.app.hardware[self.hw_name]

    def move_position_start(self, h,v):
        self.stage.settings['x_target_position'] = h
        self.stage.settings['y_target_position'] = v

    def move_position_slow(self, h, v, dh, dv):
        self.move_position_start(h,v)
    
    def move_position_fast(self, h,v,dh,dv):
        self.move_position_start(h,v)