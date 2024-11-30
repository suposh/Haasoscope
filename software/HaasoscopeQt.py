# -*- coding: utf-8 -*-
"""
pyqtgraph widget with UI template created with Qt Designer
"""

import sys, time
import h5py
import numpy as np
import pyqtgraph as pg
from serial import SerialException
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui, loadUiType
import FFTWindow
import PersistWindow




# Define main window class from template
WindowTemplate, TemplateBaseClass = loadUiType("Haasoscope.ui")
class MainWindow(TemplateBaseClass):
    def __init__(self):
        TemplateBaseClass.__init__(self)
        
        # Create the main window
        self.ui = WindowTemplate()
        self.ui.setupUi(self)
        self.ui.runButton.clicked.connect(self.dostartstop)
        self.ui.actionRecord.triggered.connect(self.record)
        self.ui.verticalSlider.valueChanged.connect(self.triggerlevelchanged)
        self.ui.verticalSlider2.valueChanged.connect(self.triggerlevel2changed)
        self.ui.thresh2Check.clicked.connect(self.thresh2)
        self.ui.horizontalSlider.valueChanged.connect(self.triggerposchanged)
        self.ui.rollingButton.clicked.connect(self.rolling)
        self.ui.singleButton.clicked.connect(self.single)
        self.ui.timeslowButton.clicked.connect(self.timeslow)
        self.ui.timefastButton.clicked.connect(self.timefast)
        self.ui.risingedgeCheck.stateChanged.connect(self.risingfalling)
        self.ui.exttrigCheck.stateChanged.connect(self.exttrig)
        self.ui.totBox.valueChanged.connect(self.tot)
        self.ui.coinBox.valueChanged.connect(self.coin)
        self.ui.cointimeBox.valueChanged.connect(self.cointime)
        self.ui.autorearmCheck.stateChanged.connect(self.autorearm)
        self.ui.noselftrigCheck.stateChanged.connect(self.noselftrig)
        self.ui.avgCheck.stateChanged.connect(self.avg)
        self.ui.logicCheck.stateChanged.connect(self.logic)
        self.ui.highresCheck.stateChanged.connect(self.highres)
        self.ui.usb2Check.stateChanged.connect(self.usb2)
        self.ui.gridCheck.stateChanged.connect(self.grid)
        self.ui.markerCheck.stateChanged.connect(self.marker)
        self.ui.resampBox.valueChanged.connect(self.resamp)
        self.ui.upposButton.clicked.connect(self.uppos)
        self.ui.downposButton.clicked.connect(self.downpos)
        self.ui.chanBox.valueChanged.connect(self.selectchannel)
        self.ui.dacBox.valueChanged.connect(self.setlevel)
        self.ui.minidisplayCheck.stateChanged.connect(self.minidisplay)
        self.ui.acdcCheck.stateChanged.connect(self.acdc)
        self.ui.gainCheck.stateChanged.connect(self.gain)
        self.ui.supergainCheck.stateChanged.connect(self.supergain)
        self.ui.actionRead_from_file.triggered.connect(self.actionRead_from_file)
        self.ui.actionStore_to_file.triggered.connect(self.actionStore_to_file)
        self.ui.actionOutput_clk_left.triggered.connect(self.actionOutput_clk_left)
        self.ui.actionAllow_same_chan_coin.triggered.connect(self.actionAllow_same_chan_coin)
        self.ui.actionDo_autocalibration.triggered.connect(self.actionDo_autocalibration)
        self.ui.chanonCheck.stateChanged.connect(self.chanon)
        self.ui.slowchanonCheck.stateChanged.connect(self.slowchanon)
        self.ui.trigchanonCheck.stateChanged.connect(self.trigchanon)
        self.ui.oversampCheck.clicked.connect(self.oversamp)
        self.ui.overoversampCheck.clicked.connect(self.overoversamp)
        self.ui.decodeCheck.clicked.connect(self.decode)
        self.ui.fftCheck.clicked.connect(self.fft)
        self.ui.persistCheck.clicked.connect(self.persist)
        self.ui.drawingCheck.clicked.connect(self.drawing)
        self.db=False
        self.lastTime = time.time()
        self.fps = None
        self.lines = []
        self.otherlines = []
        self.savetofile=False # save scope data to file
        self.doh5=False # use the h5 binary file format
        self.numrecordeventsperfile=1000 # number of events in each file to record before opening new file
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer2 = QtCore.QTimer()
        self.timer2.timeout.connect(self.drawtext)
        self.selectchannel()
        self.ui.statusBar.showMessage("Hello!")
        self.ui.plot.setBackground('w')
        self.show()

    def selectchannel(self):
        scope.selectedchannel=self.ui.chanBox.value()
        self.ui.dacBox.setValue(scope.chanlevel[scope.selectedchannel].astype(int))
        
        if scope.chanforscreen == scope.selectedchannel:   self.ui.minidisplayCheck.setCheckState(QtCore.Qt.Checked)
        else:   self.ui.minidisplayCheck.setCheckState(QtCore.Qt.Unchecked)
        if scope.acdc[scope.selectedchannel]:   self.ui.acdcCheck.setCheckState(QtCore.Qt.Unchecked)
        else:   self.ui.acdcCheck.setCheckState(QtCore.Qt.Checked)
        if scope.gain[scope.selectedchannel]:   self.ui.gainCheck.setCheckState(QtCore.Qt.Unchecked)
        else:   self.ui.gainCheck.setCheckState(QtCore.Qt.Checked)
        if scope.supergain[scope.selectedchannel]:   self.ui.supergainCheck.setCheckState(QtCore.Qt.Unchecked)
        else:   self.ui.supergainCheck.setCheckState(QtCore.Qt.Checked)
        if scope.havereadswitchdata: self.ui.supergainCheck.setEnabled(False)
        
        chanonboard = scope.selectedchannel%HaasoscopeLibQt.num_chan_per_board
        theboard = HaasoscopeLibQt.num_board-1-int(scope.selectedchannel/HaasoscopeLibQt.num_chan_per_board)
        if trigboardport!="" and trigboardport!="auto" and trigboard.extclock:
            if trigboard.histostosend != theboard: trigboard.set_histostosend(theboard)

        if scope.havereadswitchdata:
            if scope.testBit(scope.switchpos[theboard],chanonboard):   self.ui.ohmCheck.setCheckState(QtCore.Qt.Unchecked)
            else:   self.ui.ohmCheck.setCheckState(QtCore.Qt.Checked)
            
        if scope.dousb:   self.ui.usb2Check.setCheckState(QtCore.Qt.Checked)
        else:   self.ui.usb2Check.setCheckState(QtCore.Qt.Unchecked)
        
        if len(self.lines)>0:
            if self.lines[scope.selectedchannel].isVisible():   self.ui.chanonCheck.setCheckState(QtCore.Qt.Checked)
            else:   self.ui.chanonCheck.setCheckState(QtCore.Qt.Unchecked)
        if scope.trigsactive[scope.selectedchannel]:   self.ui.trigchanonCheck.setCheckState(QtCore.Qt.Checked)
        else:   self.ui.trigchanonCheck.setCheckState(QtCore.Qt.Unchecked)
        
        if scope.dooversample[scope.selectedchannel]>0:   self.ui.oversampCheck.setCheckState(QtCore.Qt.Checked)
        else:   self.ui.oversampCheck.setCheckState(QtCore.Qt.Unchecked)
        if scope.selectedchannel%HaasoscopeLibQt.num_chan_per_board>1:   self.ui.oversampCheck.setEnabled(False)
        else:  self.ui.oversampCheck.setEnabled(True)
        
        if scope.dooversample[scope.selectedchannel]>=9:   self.ui.overoversampCheck.setCheckState(QtCore.Qt.Checked)
        else:   self.ui.overoversampCheck.setCheckState(QtCore.Qt.Unchecked)
        if scope.selectedchannel%HaasoscopeLibQt.num_chan_per_board>0:  self.ui.overoversampCheck.setEnabled(False)
        else:   self.ui.overoversampCheck.setEnabled(True)
    
    def oversamp(self):
        if scope.oversamp(scope.selectedchannel)>=0:
            self.prepareforsamplechange()
            self.timechanged()
            if scope.dooversample[scope.selectedchannel] > 0:
                #turn off chan+2
                self.lines[scope.selectedchannel+2].setVisible(False)
                if scope.trigsactive[scope.selectedchannel+2]: scope.toggletriggerchan(scope.selectedchannel+2)
            else:
                # turn on chan+2
                self.lines[scope.selectedchannel + 2].setVisible(True)
                if not scope.trigsactive[scope.selectedchannel + 2]: scope.toggletriggerchan(scope.selectedchannel + 2)
    
    def overoversamp(self):
        if scope.overoversamp()>=0:
            self.prepareforsamplechange()
            self.timechanged()
            #turn off chan+1
            self.lines[scope.selectedchannel+1].setVisible(False)
            if scope.trigsactive[scope.selectedchannel+1]: scope.toggletriggerchan(scope.selectedchannel+2)
    
    def chanon(self):
        if self.ui.chanonCheck.checkState() == QtCore.Qt.Checked:
            self.lines[scope.selectedchannel].setVisible(True)
            self.ui.trigchanonCheck.setCheckState(QtCore.Qt.Checked)
        else:
            self.lines[scope.selectedchannel].setVisible(False)
            self.ui.trigchanonCheck.setCheckState(QtCore.Qt.Unchecked)
        
    def trigchanon(self):
        if self.ui.trigchanonCheck.checkState() == QtCore.Qt.Checked:
            if not scope.trigsactive[scope.selectedchannel]: scope.toggletriggerchan(scope.selectedchannel)
        else:
            if scope.trigsactive[scope.selectedchannel]: scope.toggletriggerchan(scope.selectedchannel)
    
    def slowchanon(self):
        maxchan=self.ui.slowchanBox.value()+HaasoscopeLibQt.num_chan_per_board*HaasoscopeLibQt.num_board
        if self.ui.slowchanonCheck.checkState() == QtCore.Qt.Checked:
            self.lines[maxchan].setVisible(True)
        else:
            self.lines[maxchan].setVisible(False)
    
    def acdc(self):
        if self.ui.acdcCheck.checkState() == QtCore.Qt.Checked: #ac coupled
            if scope.acdc[scope.selectedchannel]:
                scope.setacdc()
        if self.ui.acdcCheck.checkState() == QtCore.Qt.Unchecked: #dc coupled
            if not scope.acdc[scope.selectedchannel]:
                scope.setacdc()
    
    def gain(self):
        if self.ui.gainCheck.checkState() == QtCore.Qt.Checked: #x10
            if scope.gain[scope.selectedchannel]:
                scope.tellswitchgain(scope.selectedchannel)
        if self.ui.gainCheck.checkState() == QtCore.Qt.Unchecked: #x1
            if not scope.gain[scope.selectedchannel]:
                scope.tellswitchgain(scope.selectedchannel)
 
    def supergain(self):
        if self.ui.supergainCheck.checkState() == QtCore.Qt.Checked: #x100
            if scope.supergain[scope.selectedchannel]:
                scope.togglesupergainchan(scope.selectedchannel)
        if self.ui.supergainCheck.checkState() == QtCore.Qt.Unchecked: #x1
            if not scope.supergain[scope.selectedchannel]:
                scope.togglesupergainchan(scope.selectedchannel)
                   
    def minidisplay(self):
        if self.ui.minidisplayCheck.checkState()==QtCore.Qt.Checked:
            if scope.chanforscreen != scope.selectedchannel:
                scope.tellminidisplaychan(scope.selectedchannel)

    def posamount(self):
        amount=10
        modifiers = app.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            amount*=5
        elif modifiers == QtCore.Qt.ControlModifier:
            amount/=10
        return amount
    def uppos(self):
        scope.adjustvertical(True,self.posamount())
        self.ui.dacBox.setValue(scope.chanlevel[scope.selectedchannel].astype(int))
    def downpos(self):
        scope.adjustvertical(False,self.posamount())
        self.ui.dacBox.setValue(scope.chanlevel[scope.selectedchannel].astype(int))
    def setlevel(self):
        if scope.chanlevel[scope.selectedchannel] != self.ui.dacBox.value():
            scope.chanlevel[scope.selectedchannel] = self.ui.dacBox.value()
            scope.rememberdacvalue()
            scope.setdacvalue()
    
    def wheelEvent(self, event): #QWheelEvent
        if hasattr(event,"delta"):
            if event.delta()>0: self.uppos()
            else: self.downpos()
        elif hasattr(event,"angleDelta"):
            if event.angleDelta()>0: self.uppos()
            else: self.downpos()
    
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Up: self.uppos()
        if event.key()==QtCore.Qt.Key_Down: self.downpos()
        if event.key()==QtCore.Qt.Key_Left: self.timefast()
        if event.key()==QtCore.Qt.Key_Right: self.timeslow()
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if event.key()==QtCore.Qt.Key_I:
            if not modifiers == QtCore.Qt.ShiftModifier:
                theboard = HaasoscopeLibQt.num_board - 1 - int(scope.selectedchannel / HaasoscopeLibQt.num_chan_per_board)
                scope.increment_clk_phase(theboard)
            else:
                if trigboardport!="": trigboard.increment_trig_board_clock_phase()
        if event.key()==QtCore.Qt.Key_1: trigboard.set_prescale(0.1)
        if event.key()==QtCore.Qt.Key_2: trigboard.set_prescale(0.2)
        if event.key()==QtCore.Qt.Key_C: scope.toggle_checkfastusbwriting()

    def actionRead_from_file(self):
        scope.readcalib()
        
    def actionStore_to_file(self):
        scope.storecalib()

    def actionDo_autocalibration(self):
        print("starting autocalibration")
        scope.autocalibchannel=0

    def actionOutput_clk_left(self):
        scope.toggle_clk_last()
        if trigboardport!="": trigboard.setclock(True)

    def actionAllow_same_chan_coin(self):
        scope.toggle_allow_same_chan_coin()

    def exttrig(self):
        scope.toggleuseexttrig()
         
    def tot(self):
        scope.triggertimethresh = self.ui.totBox.value()
        scope.settriggertime(scope.triggertimethresh)

    def coin(self):
        scope.settrigcoin(self.ui.coinBox.value())
    def cointime(self):
        scope.settrigcointime(self.ui.cointimeBox.value())
        
    def autorearm(self):
        scope.toggleautorearm()

    def noselftrig(self):
        scope.donoselftrig()

    def avg(self):
        scope.average = not scope.average
        print("average",scope.average)
        
    def logic(self):
        scope.togglelogicanalyzer()
        if scope.dologicanalyzer:
            for li in np.arange(scope.num_logic_inputs):
                c=(0,0,0)
                pen = pg.mkPen(color=c) # add linewidth=1.7, alpha=.65
                self.lines[scope.logicline1+li].setPen(pen)
        else:
            for li in np.arange(scope.num_logic_inputs):
                self.lines[scope.logicline1+li].setPen(None)
        
    def highres(self):
        scope.togglehighres()
        
    def usb2(self):
        if self.ui.usb2Check.checkState() == QtCore.Qt.Checked:
            if not scope.dousb:
                scope.toggledousb()
        else:
            if scope.dousb:
                scope.toggledousb()
        
    def grid(self):
        if self.ui.gridCheck.isChecked():
            self.ui.plot.showGrid(x=True, y=True)
        else:
            self.ui.plot.showGrid(x=False, y=False)
            
    def marker(self):
        if self.ui.markerCheck.isChecked():
            for li in range(self.nlines):
                self.lines[li].setSymbol("o")
                self.lines[li].setSymbolSize(3)
                #self.lines[li].setSymbolPen("black")
                self.lines[li].setSymbolPen(self.linepens[li].color())
                self.lines[li].setSymbolBrush(self.linepens[li].color())
        else:
            for li in range(self.nlines):
                self.lines[li].setSymbol(None)
                
    def resamp(self):
        scope.sincresample = self.ui.resampBox.value()
        if scope.sincresample>0: scope.xydata=np.empty([HaasoscopeLibQt.num_chan_per_board*HaasoscopeLibQt.num_board,2,scope.sincresample*(scope.num_samples-1)],dtype=float)
        else: scope.xydata=np.empty([HaasoscopeLibQt.num_chan_per_board*HaasoscopeLibQt.num_board,2,1*(scope.num_samples-1)],dtype=float)
        self.prepareforsamplechange()
    
    def dostartstop(self):        
        if scope.paused:
            self.timer.start(0)
            self.timer2.start(1000)
            scope.paused=False
            self.ui.runButton.setChecked(True)            
        else:
            self.timer.stop()
            self.timer2.stop()
            scope.paused=True
            self.ui.runButton.setChecked(False)
    
    def prepareforsamplechange(self): #called when sampling is changed, to reset some things
        scope.recordedchannel=[]
        #if d.doxyplot: plt.close(self.figxy)
        #if d.recorddata: plt.close(self.fig2d)
        
    def triggerlevelchanged(self,value):
        scope.settriggerthresh(value)
        self.hline = (float(  value-128  )*scope.yscale/256.)
        self.otherlines[1].setData( [scope.min_x, scope.max_x], [self.hline, self.hline] ) # horizontal line showing trigger threshold

    def triggerlevel2changed(self,value):
        scope.settriggerthresh2(value)                
        self.hline2 =(float(  value-128  )*scope.yscale/256.)
        self.otherlines[2].setVisible(True) # starts off being hidden, so now show it!
        self.otherlines[2].setData( [scope.min_x, scope.max_x], [self.hline2, self.hline2] )
        
    def thresh2(self):
        if self.ui.thresh2Check.checkState() == QtCore.Qt.Checked:
            self.ui.verticalSlider2.setEnabled(True)
            self.otherlines[2].setVisible(True)
        else:
            self.ui.verticalSlider2.setValue(0)
            self.ui.verticalSlider2.setEnabled(False)
            self.otherlines[2].setVisible(False)
    
    def triggerposchanged(self,value):
        if value>253 or value<3: return
        offset=5.0 # trig to readout delay
        scal = scope.num_samples/256.
        point = value*scal + offset/pow(2,scope.downsample)
        if scope.downsample<0: point = 128*scal + (point-128*scal)*pow(2,scope.downsample)
        scope.settriggerpoint(int(point))
        self.vline = float(  2*(value-128)/256. *scope.xscale /scope.xscaling)
        self.otherlines[0].setData( [self.vline, self.vline], [scope.min_y, scope.max_y] ) # vertical line showing trigger time
    
    def rolling(self):
        scope.rolltrigger = not scope.rolltrigger
        scope.tellrolltrig(scope.rolltrigger)
        if trigboardport!="":
            trigboard.togglerolling()
        self.ui.rollingButton.setChecked(scope.rolltrigger)
        if scope.rolltrigger: self.ui.rollingButton.setText("Rolling/Auto")
        else: self.ui.rollingButton.setText("Normal")

    def single(self):
        scope.getone = not scope.getone
        self.ui.singleButton.setChecked(scope.getone)
        
    def timefast(self):
        amount=1
        modifiers = app.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            amount*=5
        scope.telldownsample(scope.downsample-amount)
        self.timechanged()
    
    def timeslow(self):
        amount=1
        modifiers = app.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            amount*=5
        scope.telldownsample(scope.downsample+amount)
        self.timechanged()
    
    def timechanged(self):
        self.ui.plot.setRange(xRange=(scope.min_x, scope.max_x), yRange=(scope.min_y, scope.max_y)) 
        self.ui.plot.setMouseEnabled(x=False,y=False)
        self.ui.plot.setLabel('bottom', scope.xlabel)
        self.ui.plot.setLabel('left', scope.ylabel)
        self.triggerposchanged(self.ui.horizontalSlider.value())
        self.ui.timebaseBox.setText("downsample "+str(scope.downsample))
        
    def risingfalling(self):
        scope.fallingedge=not self.ui.risingedgeCheck.checkState()
        scope.settriggertype(scope.fallingedge)

    def decode(self):
        if self.ui.decodeCheck.checkState() != QtCore.Qt.Checked:
            # delete all previous labels
            for label in self.decodelabels:
                self.ui.plot.removeItem(label)

    def fft(self):
        if self.ui.fftCheck.checkState() == QtCore.Qt.Checked:
            scope.fftchan = scope.selectedchannel
            self.fftui = FFTWindow()
            self.fftui.setWindowTitle('HaasoscopeQt FFT of channel ' + str(scope.fftchan))
            self.fftui.show()
            scope.dofft = True
        else:
            self.fftui.close()
            scope.dofft = False

    def persist(self):
        if self.ui.persistCheck.checkState() == QtCore.Qt.Checked:
            self.persistui = PersistWindow()
            self.persistui.setWindowTitle('HaasoscopeQt persist of channel ' + str(scope.selectedchannel))
            self.persistui.show()
            scope.recorddata=True; scope.recorddatachan=scope.selectedchannel; scope.recordedchannel=[]
            self.firstpersist=True
            print("recorddata now",scope.recorddata,"for channel",scope.recorddatachan)
        else:
            scope.recorddata=False; scope.recorddatachan=scope.selectedchannel; scope.recordedchannel=[]
            print("recorddata now",scope.recorddata)
            self.persistui.close()

    def drawing(self):
        if self.ui.drawingCheck.checkState() == QtCore.Qt.Checked:
            scope.dodrawing=True
            print("drawing now",scope.dodrawing)
        else:
            scope.dodrawing=False
            print("drawing now",scope.dodrawing)

    def record(self):
        self.savetofile = not self.savetofile
        if self.savetofile:
            fname="xxx"
            if self.doh5:
                fname="Haasoscope_out_" + time.strftime("%Y%m%d-%H%M%S") + ".h5"
                self.outf = h5py.File(fname,"w")
            else:
                fname="Haasoscope_out_" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
                self.outf = open(fname,"wt")
            self.ui.statusBar.showMessage("now recording to file: "+fname)
            self.ui.actionRecord.setText("Stop recording")
        else:
            self.outf.close()
            self.ui.statusBar.showMessage("stopped recording to file")
            self.ui.actionRecord.setText("Record to file")
    
    def fastadclineclick(self, curve):
        for li in range(self.nlines):
            if curve is self.lines[li].curve:
                maxchan=li-HaasoscopeLibQt.num_chan_per_board*HaasoscopeLibQt.num_board
                if maxchan>=0: # these are the slow ADC channels
                    self.ui.slowchanBox.setValue(maxchan)
                    #print "selected slow curve", maxchan
                else:
                    self.ui.chanBox.setValue(li)
                    #print "selected curve", li
                    modifiers = app.keyboardModifiers()
                    if modifiers == QtCore.Qt.ShiftModifier:
                        self.ui.trigchanonCheck.toggle()
                    elif modifiers == QtCore.Qt.ControlModifier:
                        self.ui.chanonCheck.toggle()
    
    """ TODO:       
            elif event.key=="ctrl+r": 
                if self.ydatarefchan<0: self.ydatarefchan=self.selectedchannel
                else: self.ydatarefchan=-1
            elif event.key==">": self.refsinchan=self.selectedchannel; self.oldchanphase=-1.; self.reffreq=0;
            elif event.key=="Y": 
                if self.selectedchannel+1>=len(self.dooversample): print "can't do XY plot on last channel"
                else:
                    if self.dooversample[self.selectedchannel]==self.dooversample[self.selectedchannel+1]:
                        self.doxyplot=True; self.xychan=self.selectedchannel; print "doxyplot now",self.doxyplot,"for channel",self.xychan; return;
                    else: print "oversampling settings must match between channels for XY plotting"
    """
    
    linepens=[]
    def launch(self):        
        self.nlines = HaasoscopeLibQt.num_chan_per_board*HaasoscopeLibQt.num_board+len(HaasoscopeLibQt.max10adcchans)
        if self.db: print("nlines=",self.nlines)
        for li in np.arange(self.nlines):
            maxchan=li-HaasoscopeLibQt.num_chan_per_board*HaasoscopeLibQt.num_board
            c=(0,0,0)
            if maxchan>=0: # these are the slow ADC channels
                if HaasoscopeLibQt.num_board>1:
                    board = int(HaasoscopeLibQt.num_board-1-HaasoscopeLibQt.max10adcchans[maxchan][0])
                    if board % 4 == 0: c = (255 - 0.2 * 255 * maxchan, 0, 0)
                    if board % 4 == 1: c = (0, 255 - 0.2 * 255 * maxchan, 0)
                    if board % 4 == 2: c = (0, 0, 255 - 0.2 * 255 * maxchan)
                    if board % 4 == 3: c = (255 - 0.2 * 255 * maxchan, 0, 255 - 0.2 * 255 * maxchan)
                else:
                    c=(0.1*(maxchan+1),0.1*(maxchan+1),0.1*(maxchan+1))
                pen = pg.mkPen(color=c) # add linewidth=0.5, alpha=.5
                line = self.ui.plot.plot(pen=pen,name="slowadc_"+str(HaasoscopeLibQt.max10adcchans[maxchan]))
            else: # these are the fast ADC channels
                chan=li%4
                board=int(li/4)
                if self.db: print("chan =",chan,"and board =",board)
                if HaasoscopeLibQt.num_board>1:                    
                    if board%4==0: c=(255-0.2*255*chan,0,0)
                    if board%4==1: c=(0,255-0.2*255*chan,0)
                    if board%4==2: c=(0,0,255-0.2*255*chan)
                    if board%4==3: c=(255-0.2*255*chan,0,255-0.2*255*chan)
                else:
                    if chan==0: c="r"
                    if chan==1: c="g"
                    if chan==2: c="b"
                    if chan==3: c="m"
                pen = pg.mkPen(color=c) # add linewidth=1.0, alpha=.9
                line = self.ui.plot.plot(pen=pen,name=scope.chtext+str(li))
            line.curve.setClickable(True)
            line.curve.sigClicked.connect(self.fastadclineclick)
            self.lines.append(line)
            self.linepens.append(pen)
        self.ui.chanBox.setMaximum(HaasoscopeLibQt.num_chan_per_board*HaasoscopeLibQt.num_board-1)
        self.ui.slowchanBox.setMinimum(0)
        self.ui.slowchanBox.setMaximum(max(len(HaasoscopeLibQt.max10adcchans)-1,0))
        #for the logic analyzer
        for li in np.arange(scope.num_logic_inputs):
            line = self.ui.plot.plot(pen=None,name="logic_"+str(li)) # not drawn by default
            self.lines.append(line)
            if li==0: scope.logicline1=len(self.lines)-1 # remember index where this first logic line is
        #other data to draw
        if scope.fitline1>-1:
            pen = pg.mkPen(color="purple") # add linewidth=0.5, alpha=.5
            line = self.ui.plot.plot(pen=pen,name="fitline1") # not drawn by default
            line.setVisible(False)
            self.lines.append(line)
            scope.fitline1=len(self.lines)-1 # remember index where this line is
        #trigger lines
        self.vline=0.0
        pen = pg.mkPen(color="k",width=1.0,style=QtCore.Qt.DashLine)
        line = self.ui.plot.plot([self.vline, self.vline], [-2.0, 2.0], pen=pen,name="trigger time vert")
        self.otherlines.append(line)
        self.hline = 0.0
        pen = pg.mkPen(color="k",width=1.0,style=QtCore.Qt.DashLine)
        line = self.ui.plot.plot( [-2.0, 2.0], [self.hline, self.hline], pen=pen,name="trigger thresh horiz")
        self.otherlines.append(line)
        self.hline2 = 0.0
        pen = pg.mkPen(color="b",width=1.0,style=QtCore.Qt.DashLine)
        line = self.ui.plot.plot( [-2.0, 2.0], [self.hline2, self.hline2], pen=pen,name="trigger thresh2 horiz") # not drawn by default
        line.setVisible(False)
        self.otherlines.append(line)
        #other stuff
        scope.setxaxis()
        scope.setyaxis()
        self.timechanged()
        self.ui.totBox.setMaximum(scope.num_samples)
        self.ui.plot.showGrid(x=True, y=True)
    
    def closeEvent(self, event):
        print("Handling closeEvent")
        self.timer.stop()
        self.timer2.stop()
        if trigboardport!="": trigboard.cleanup()
        scope.cleanup()
        if self.savetofile: self.outf.close()
        if hasattr(self,"fftui"):
            self.fftui.close()
        if hasattr(self,"persistui"):
            self.persistui.close()

    decodelabels = []
    def updateplot(self):
        self.mainloop()
        if scope.timedout: return # don't draw old junk if there was a timeout getting data (as often the case with no rolling trigger)
        if self.savetofile: self.dosavetofile()
        if not self.ui.drawingCheck.checkState() == QtCore.Qt.Checked: return
        for li in range(self.nlines):
            maxchan=li-HaasoscopeLibQt.num_chan_per_board*HaasoscopeLibQt.num_board
            if maxchan>=0: # these are the slow ADC channels
                self.lines[li].setData(scope.xydataslow[maxchan][0],scope.xydataslow[maxchan][1])
            else:
                self.lines[li].setData(scope.xydata[li][0],scope.xydata[li][1])
        if scope.dologicanalyzer:
            for li in np.arange(scope.num_logic_inputs):
                self.lines[scope.logicline1+li].setData(scope.xydatalogic[li][0],scope.xydatalogic[li][1])
        if scope.dofft:
            self.fftui.fftline.setPen(self.linepens[scope.fftchan])
            self.fftui.fftline.setData(scope.fftfreqplot_xdata,scope.fftfreqplot_ydata)
            self.fftui.ui.plot.setTitle("FFT plot of channel "+str(scope.fftchan))
            self.fftui.ui.plot.setLabel('bottom', scope.fftax_xlabel)
            self.fftui.ui.plot.setRange(xRange=(0.0, scope.fftax_xlim))
            now = time.time()
            dt = now - self.fftui.fftlastTime
            if dt>3.0 or self.fftyrange<scope.fftfreqplot_ydatamax*1.1:
                self.fftui.fftlastTime = now
                self.fftui.ui.plot.setRange(yRange=(0.0, scope.fftfreqplot_ydatamax*1.1))
                self.fftyrange = scope.fftfreqplot_ydatamax * 1.1
            if not self.fftui.isVisible(): # closed the fft window
                scope.dofft = False
                self.ui.fftCheck.setCheckState(QtCore.Qt.Unchecked)
        if scope.recorddata:
            if self.firstpersist:
                self.image1 = pg.ImageItem(image=scope.recorded2d,opacity=0.5)
                self.persistui.ui.plot.addItem(self.image1)
                self.persistui.ui.plot.setTitle("Persist plot of channel "+str(scope.recorddatachan))
                self.cmap = pg.colormap.get('CET-D8')
                self.firstpersist=False
            else:
                self.image1.setImage(image=scope.recorded2d,opacity=0.5)
            self.image1.setRect(QtCore.QRectF(scope.min_x,scope.min_y,scope.max_x-scope.min_x,scope.max_y-scope.min_y))
            self.persistui.ui.plot.setLabel('bottom', scope.xlabel)
            self.bar = pg.ColorBarItem(interactive=False, values= (0, np.max(scope.recorded2d)), cmap=self.cmap)
            self.bar.setImageItem(self.image1)
            if not self.persistui.isVisible(): # closed the fft window
                scope.recorddata = False
                self.ui.persistCheck.setCheckState(QtCore.Qt.Unchecked)
        if self.ui.decodeCheck.checkState() == QtCore.Qt.Checked:
            # delete all previous labels
            for label in self.decodelabels:
                self.ui.plot.removeItem(label)
            if scope.downsample>=0:
                resulttext,resultstart,resultend = scope.decode()
                #print(resulttext,resultstart, d.min_x, d.max_x, d.xscale, d.xscaling)
                item=0
                while item<len(resulttext):
                    label = pg.TextItem(resulttext[item])
                    label.setColor(self.linepens[scope.selectedchannel].color())
                    x=scope.min_x+resultstart[item]*1e9/scope.xscaling
                    label.setPos( QtCore.QPointF(x, -1) )
                    #print(x)
                    self.ui.plot.addItem(label)
                    self.decodelabels.append(label)
                    item=item+1
            else:
                print("can't decode when downsample is <0... go slower!")
        now = time.time()
        dt = now - self.lastTime + 0.00001
        self.lastTime = now
        if self.fps is None:
            self.fps = 1.0/dt
        else:
            s = np.clip(dt*3., 0, 1)
            self.fps = self.fps * (1-s) + (1.0/dt) * s
        self.ui.plot.setTitle('%0.2f fps' % self.fps)
        app.processEvents()

    oldxscale=0
    def dosavetofile(self):
        time_s=str(time.time())
        if self.doh5:
            datatosave=scope.xydata[:,1,:] # save all y data by default
            if scope.xscale != self.oldxscale:
                datatosave=scope.xydata # since the x scale changed (or is the first event), save all data for this event
                self.oldxscale=scope.xscale
            h5ds = self.outf.create_dataset(str(self.nevents), data=datatosave, dtype='float32', compression="lzf") #compression="gzip", compression_opts=5)
            #about 3kB per event per board (4 channels) for 512 samples
            h5ds.attrs['time']=time_s
            h5ds.attrs['trigger_position']=str(self.vline*scope.xscaling)
            h5ds.attrs['sample_period'] =str(2.*scope.xscale/scope.num_samples)
            h5ds.attrs['num_samples'] =str(scope.num_samples)
            if scope.dologicanalyzer: h5ds = self.outf.create_dataset(str(self.nevents)+"_logic", data=scope.xydatalogicraw, dtype='uint8', compression="lzf")
            # see h5py_analyze_example.py for how to read in python
        else:
            for c in range(HaasoscopeLibQt.num_chan_per_board*HaasoscopeLibQt.num_board):
                if self.lines[c].isVisible(): # only save the data for visible channels
                    self.outf.write(str(self.nevents)+",") # start of each line is the event number
                    self.outf.write(time_s+",") # next column is the time in seconds of the current event
                    self.outf.write(str(c)+",") # next column is the channel number
                    self.outf.write(str(self.vline*scope.xscaling)+",") # next column is the trigger time
                    self.outf.write(str(2.*scope.xscale/scope.num_samples)+",") # next column is the time between samples, in ns
                    self.outf.write(str(scope.num_samples)+",") # next column is the number of samples
                    scope.xydata[c][1].tofile(self.outf,",",format="%.3f") # save y data (1) from fast adc channel c
                    self.outf.write("\n") # newline
            if scope.dologicanalyzer:
                for b in range(HaasoscopeLibQt.num_board):
                    scope.xydatalogicraw[b].tofile(self.outf,",")
                    self.outf.write("\n")  # newline
        # should also write out the 8 digital bits per board (if logic analyzer on)
        # stored in d.xydatalogicraw[board]
    
    nevents=0
    oldnevents=0
    tinterval=100.
    oldtime=time.time()
    def mainloop(self):
        if scope.paused: time.sleep(.1)
        else:
            try: status=scope.getchannels()
            except SerialException:
                print("Serial exception getting channels!!")
                sys.exit(1)
            except DeviceError:
                print("Device error")
                sys.exit(1)
            if status==2: self.selectchannel() #we updated the switch data
            if scope.db: print(time.time()-scope.oldtime,"done with evt",self.nevents)
            self.nevents += 1
            if self.nevents-self.oldnevents >= self.tinterval:
                now=time.time()
                elapsedtime=now-self.oldtime
                self.oldtime=now
                lastrate = round(self.tinterval/elapsedtime,2)
                if scope.dologicanalyzer: nchan = HaasoscopeLibQt.num_chan_per_board + 1
                else: nchan = HaasoscopeLibQt.num_chan_per_board
                print(self.nevents,"events,",lastrate,"Hz",round(lastrate*HaasoscopeLibQt.num_board*scope.num_samples*nchan/1e6,3),"MB/s")
                if lastrate>40: self.tinterval=500.
                else: self.tinterval=100.
                self.oldnevents=self.nevents
                newrecordedchannellength=int(max(10,5*lastrate)) #the number of events to show on the persist plot
                if newrecordedchannellength<len(scope.recordedchannel):
                    del scope.recordedchannel[0:len(scope.recordedchannel)-newrecordedchannellength]
                scope.recordedchannellength=newrecordedchannellength
            if self.nevents%self.numrecordeventsperfile==0:
                if self.savetofile: # if writing, close and open new file
                    self.record()
                    if self.doh5: self.oldxscale=0 #to force writing the time header info in h5
                    self.record()
            if scope.getone and not scope.timedout: self.dostartstop()

    def drawtext(self): # happens once per second
        scope.tellrolltrig(scope.rolltrigger) #because sometimes the message had been lost
        self.ui.textBrowser.setText(scope.chantext())
        self.ui.textBrowser.append("trigger threshold: " + str(round(self.hline,3)))
        if trigboardport!="" and trigboard.extclock:
            delaycounters = trigboard.get_delaycounters()
            self.ui.textBrowser.append("delay counters: "+str(delaycounters))
            self.ui.textBrowser.append(trigboard.get_histos())
            for b in range(HaasoscopeLibQt.num_board):
                if not delaycounters[b]:
                    scope.increment_clk_phase(b,30) # increment clk of that board by 30*100ps=3ns

if __name__ == '__main__':
    import libs.HaasoscopeLibQt as HaasoscopeLibQt
    import libs.HaasoscopeTrigLibQt as HaasoscopeTrigLibQt

    print('Argument List:', str(sys.argv))
    for a in sys.argv:
        if a[0] == "-":
            #print(a)
            if a[1:3] == "sr": #eg: -sr4
                slowadc_ram_width = int(a[3:])
                if slowadc_ram_width > HaasoscopeLibQt.max_slowadc_ram_width:
                    print("slowadc_ram_width", slowadc_ram_width, "too large")
                elif slowadc_ram_width < 1:
                    print("slowadc_ram_width", slowadc_ram_width, "too small")
                else:
                    HaasoscopeLibQt.slowadc_ram_width = slowadc_ram_width
                    print("slowadc_ram_width set to", HaasoscopeLibQt.slowadc_ram_width)
            elif a[1:4] == "adc": #eg: -adc[(0,110),(0,118)]
                exec("HaasoscopeLibQt.max10adcchans=" + a[4:])
                print("max10adcchans set to", HaasoscopeLibQt.max10adcchans)
            elif a[1] == "r": #eg: -r12
                ram_width = int(a[2:])
                if ram_width > HaasoscopeLibQt.max_ram_width:
                    print("ram_width", ram_width, "is bigger than the max allowed", HaasoscopeLibQt.max_ram_width)
                    HaasoscopeLibQt.ram_width = HaasoscopeLibQt.max_ram_width
                elif ram_width < 1:
                    print("ram_width", ram_width, "is less than 1")
                    HaasoscopeLibQt.ram_width = 1
                else:
                    HaasoscopeLibQt.ram_width = ram_width
                print("ram_width set to", HaasoscopeLibQt.ram_width)
            elif a[1] == "b": #eg: -b2
                HaasoscopeLibQt.num_board = int(a[2:])
                print("num_board set to", HaasoscopeLibQt.num_board)

    scope = HaasoscopeLibQt.Haasoscope()

    script=""
    trigboardport = ""
    for a in sys.argv:
        if a[0] == "-":
            #print(a)
            if a[1:3] == "mt":
                scope.domt=True
                print("domt set to",scope.domt)
            elif a[1:8] == "fastusb":
                scope.dofastusb = True
                scope.dousbparallel = True
                print("dofastusb", scope.dofastusb, "and dousbparallel", scope.dousbparallel)
            elif a[1:7] == "script": #eg: -scriptmysetup.py will run those commands after setup
                script = str(a[7:])
                print("script set to", script)
            elif a[1] == "s" and a[2]!="r":
                scope.serialdelaytimerwait = int(a[2:])
                print("serialdelaytimerwait set to", scope.serialdelaytimerwait)
            elif a[1] == "p":
                scope.serport = a[2:]
                print("serial port manually set to", scope.serport)
            elif a[1] == "t":
                trigboardport = a[2:]
                print("trigboardport set to", trigboardport)            

    if scope.domt and not scope.dofastusb:
        print("mt option is only for fastusb - exiting!")
        sys.exit()

    print("Python version", sys.version)
    app = QtWidgets.QApplication.instance()
    standalone = app is None
    if standalone:
        #print('INSIDE STANDALONE')
        app = QtWidgets.QApplication(sys.argv)

    try:
        font = app.font();
        font.setPixelSize(11);
        app.setFont(font);
        win = MainWindow()
        win.setWindowTitle('Haasoscope Qt')
        if not scope.setup_connections():
            print("Exiting now - failed setup_connections!")
            sys.exit(1)
        if trigboardport!="":
            if trigboardport=="auto": trigboardport=scope.trigserport
            trigboard = HaasoscopeTrigLibQt.HaasoscopeTrig(trigboardport)
            if not trigboard.get_firmware_version():
                print("couldn't get trigboard firmware version - exiting!")
                sys.exit()
            trigboard.setrngseed()
            trigboard.set_prescale(1.0)
        if not scope.init():
            print("Exiting now - failed init!")
            scope.cleanup()
            sys.exit()
        win.launch()
        win.triggerposchanged(128)  # center the trigger

        if script != "":
            print("Excecuting file", script)
            exec(open(script).read())

        win.dostartstop()
    except SerialException:
        print("serial com failed!")

    if standalone:
        rv=app.exec_()
        sys.exit(rv)
    else:
        print("Done, but Qt window still active")
