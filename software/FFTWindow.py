import pyqtgraph as pg
from pyqtgraph.Qt import loadUiType

# Define fft window class from template
FFTWindowTemplate, FFTTemplateBaseClass = loadUiType("HaasoscopeFFT.ui")
class FFTWindow(FFTTemplateBaseClass):
    def __init__(self):
        FFTTemplateBaseClass.__init__(self)
        self.ui = FFTWindowTemplate()
        self.ui.setupUi(self)
        self.ui.plot.setLabel('bottom', 'Freq (MHz)')
        self.ui.plot.setLabel('left', '|Y(freq)|')
        self.ui.plot.showGrid(x=True, y=True, alpha=1.0)
        self.ui.plot.setRange(xRange=(0.0, 65.0))
        self.ui.plot.setBackground('w')
        c = (10, 10, 10)
        self.fftpen = pg.mkPen(color=c)  # add linewidth=0.5, alpha=.5
        self.fftline = self.ui.plot.plot(pen=self.fftpen, name="fft_plot")
        self.fftlastTime = time.time() - 10
        self.fftyrange = 1
