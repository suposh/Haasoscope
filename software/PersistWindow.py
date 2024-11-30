from pyqtgraph.Qt import loadUiType

# Define persist window class from template
PersistWindowTemplate, PersistTemplateBaseClass = loadUiType("HaasoscopePersist.ui")
class PersistWindow(PersistTemplateBaseClass):
    def __init__(self):
        PersistTemplateBaseClass.__init__(self)
        self.ui = PersistWindowTemplate()
        self.ui.setupUi(self)
        self.ui.plot.setLabel('bottom', 'Time')
        self.ui.plot.setLabel('left', 'Volts')
        self.ui.plot.showGrid(x=True, y=True, alpha=1.0)
        self.ui.plot.setBackground('w')