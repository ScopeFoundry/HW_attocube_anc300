from ScopeFoundry.base_app import BaseMicroscopeApp
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('PyQt5').setLevel(logging.WARN)
logging.getLogger('ipykernel').setLevel(logging.WARN)
logging.getLogger('traitlets').setLevel(logging.WARN)
logging.getLogger('LoggedQuantity').setLevel(logging.WARN)

class AttocubeTestApp(BaseMicroscopeApp):
    
    name="anc300_test_app"
    
    def setup(self):
        from ScopeFoundryHW.attocube_anc300.anc300_hw import AttocubeANC300StageHW
        self.add_hardware(AttocubeANC300StageHW(self, ax_names='xy'))
        
        from ScopeFoundryHW.attocube_anc300.anc300_slow_scan import AttocubeANC300_2DSlowScan
        self.add_measurement(AttocubeANC300_2DSlowScan(self))

        
if __name__ == '__main__':
    import sys
    app = AttocubeTestApp(sys.argv)
    sys.exit(app.exec_())   
        