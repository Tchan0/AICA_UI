# YAMAHA AICA SLOT (aka 'Channel')
# ================================
# 64 sound slots (aka channels) 
# Inputs:
#   - noise
#   - PCM (from Audio RAM): 8bit/16bit PCM, 4bit Yamaha ADPCM, 4bit ADPCM long stream
# 
# Outputs:
#   - directly to DAC (volume level: DISDL, panning: DIPAN)
#   - to DSP          (volume level: IMXL,  ISEL allows to select 1 of the 16 MIXS slots

from Qt import QtCore, QtWidgets, QtGui
from NodeGraphQt import BackdropNode, BaseNode, NodeBaseWidget
from NodeGraphQt.constants import PortTypeEnum

from aica_prot  import *
from aica_utils import *
#######################################################
# Create a backdrop node to regroup all AICA slot nodes
#######################################################
class SlotsNode(BackdropNode):
    __identifier__ = 'aica.slots'
    NODE_NAME = 'AICA Slots Node'

    def __init__(self):
        super(SlotsNode, self).__init__()
        self._active_slots = 0

    def getSlotName(self, slotnr):
        return 'AICA SLOT ' + str(slotnr)

    def add(self, mx_node): #add a slot
        if self._active_slots < 64:
            new_slot = self.graph.create_node('aica.slots.SlotNode', name=self.getSlotName(self._active_slots)) 
            new_slot.setId(self._active_slots)
            mx_node.add()
            new_slot.set_output(0, mx_node.input(self._active_slots))
            self._active_slots += 1
            #TODO: if (self._active_slots) new_slot.set_pos(x, y): set node position right underneath the previous slot

    def remove(self, mx_node): #remove a slot
        if self._active_slots > 0:
            self.graph.delete_node(self.graph.get_node_by_name(self.getSlotName(self._active_slots - 1)))
            mx_node.remove()
            self._active_slots -= 1

    def autoWrap(self): #auto-wrap around all present AICA slot nodes
        slotNodes = self.graph.get_nodes_by_type('aica.slots.SlotNode')
        #print("slotnodes count: " , str(len(slotNodes)))
        self.wrap_nodes(slotNodes)


#######################################################
# Individual AICA slot (Channel)
#######################################################
class SlotNode(BaseNode):
    __identifier__ = 'aica.slots'
    NODE_NAME = 'AICA slot'

    def __init__(self):
        super(SlotNode, self).__init__()

        # add the inputs ports
        rawPort = self.add_input('MONO_IN')
        self.add_accept_port_type(rawPort, {'port_name': 'MONO',  'port_type': PortTypeEnum.OUT.value, 'node_type': 'audio.source.AudioSourceNode'})
        self.add_accept_port_type(rawPort, {'port_name': 'LEFT',  'port_type': PortTypeEnum.OUT.value, 'node_type': 'audio.source.AudioSourceNode'})
        self.add_accept_port_type(rawPort, {'port_name': 'RIGHT', 'port_type': PortTypeEnum.OUT.value, 'node_type': 'audio.source.AudioSourceNode'})
        noisePort = self.add_input('noise')
        self.add_accept_port_type(noisePort, {'port_name': 'NOIZZ', 'port_type': PortTypeEnum.OUT.value, 'node_type': 'audio.source.AudioSourceNode'})##hack to refuse pipes to this port

        # create the output ports
        self.add_output('to_mixer')
        self.add_output('to_DSP')

        # custom widgets
        self.node_widget = SlotNodeWidgetWrapper(self.view)
        self.node_widget.setNode(self)
        self.add_custom_widget(self.node_widget, tab='Custom')

    def setId(self, slotNr):
        self.slotNr = slotNr

    #if a pipe was connected to sound input of slot XX: 
    def on_input_connected(self, in_port, out_port):
        sourceNode = out_port.node()
        #TODO? sourceNode.numSamplesPerChannel <- always 44 kHz on the Aica ????
        # sourceNode.setIsLoadedInAICARAM(1, ramADDR)
        # if sourceNode.ramADDR: #already loaded in AICA RAM, reuse -> set ramAddr if removed from all slots, so that ram can be reused
        #     AAA Slot_SetWaveDataPtrs(dest,start,end,slotNr):
        # else:
        Aica_LoadWaveData(0x00860000, int(sourceNode.numSamplesPerChannel * (sourceNode.bits / 8)), sourceNode.audioData.tobytes()) #TODO: dataBytes for 1 channel - what if stereo, send the correct channel ?
        Slot_Format(sourceNode.bits, 0, self.slotNr)
        Slot_SetWaveDataPtrs(0x00860000, 0, sourceNode.numSamplesPerChannel, self.slotNr)
        #TODO reset pitch (OCT/FNS ? -> if both 0, original sound)


    def on_input_disconnected(self, in_port, out_port):
        print("HEY, Input disconnected !")

class SlotCustomWidget(QtWidgets.QWidget):
    # Custom widget to be embedded inside a SlotNode.
    def __init__(self, parent=None):
        super(SlotCustomWidget, self).__init__(parent)
        # UI ELEMENTS
        self.SlotIsNoise  = QtWidgets.QCheckBox("Noise")
        #self.SlotIsNoise.setStyleSheet("QCheckBox { color: white }")
        self.SlotIsON     = QtWidgets.QCheckBox("ON")
        #self.SlotIsON.setStyleSheet("QCheckBox { color: white }")
        self.SlotLoopON   = QtWidgets.QCheckBox("LOOP")
        #self.SlotLoopON.setStyleSheet("QCheckBox { color: white }")
        self.DSPLabel     = QtWidgets.QLabel()
        self.DSPLabel.setText("DSP:")#self.DSPLabel.setText("<font color=white>DSP:</font>")
        self.DACLabel     = QtWidgets.QLabel()
        self.DACLabel.setText("DAC:")#self.DACLabel.setText("<font color=white>DAC:</font>")
        self.DSPLevel     = QtWidgets.QSlider(QtCore.Qt.Horizontal) #QtWidgets.QDial()
        self.DSPLevel.setRange(0,15) #self.DSPLevelDial.setSingleStep(1)
        self.DSPLevel.setTracking(0)
        self.DACLevel     = QtWidgets.QSlider(QtCore.Qt.Horizontal) #QtWidgets.QDial()
        self.DACLevel.setRange(0,15) #self.DACLevelDial.setSingleStep(1)
        self.DACLevel.setTracking(0)
        self.DACPanSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.DACPanSlider.setRange(-15, 15)
        self.DACPanSlider.setValue(0)
        self.DACPanSlider.setTracking(0)
        self.LFOOscFreq = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.LFOOscFreq.setRange(0, 31)
        self.LFOOscFreq.setValue(0)
        self.LFOOscFreq.setTracking(0)
        self.LFOReset  = QtWidgets.QCheckBox("LFO OFF")
        #self.LFOReset.setStyleSheet("QCheckBox { color: white }")
        self.ALFOLevel = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.ALFOLevel.setRange(0, 7)
        self.ALFOLevel.setValue(0)
        self.ALFOLevel.setTracking(0)
        self.ALFOShapeGrp      = QtWidgets.QButtonGroup(self)
        self.ALFOShapeSaw      = QtWidgets.QRadioButton("Saw")
        self.ALFOShapePulse    = QtWidgets.QRadioButton("Pulse")
        self.ALFOShapeTriangle = QtWidgets.QRadioButton("Triangle")
        self.ALFOShapeNoise    = QtWidgets.QRadioButton("Noise")
        self.ALFOShapeGrp.addButton(self.ALFOShapeSaw,      0)
        self.ALFOShapeGrp.addButton(self.ALFOShapePulse,    1)
        self.ALFOShapeGrp.addButton(self.ALFOShapeTriangle, 2)
        self.ALFOShapeGrp.addButton(self.ALFOShapeNoise,    3)
        self.PLFOLevel = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.PLFOLevel.setRange(0, 7)
        self.PLFOLevel.setValue(0)
        self.PLFOLevel.setTracking(0)
        self.PLFOShapeGrp      = QtWidgets.QButtonGroup(self)
        self.PLFOShapeSaw      = QtWidgets.QRadioButton("Saw")
        self.PLFOShapePulse    = QtWidgets.QRadioButton("Pulse")
        self.PLFOShapeTriangle = QtWidgets.QRadioButton("Triangle")
        self.PLFOShapeNoise    = QtWidgets.QRadioButton("Noise")
        self.PLFOShapeGrp.addButton(self.PLFOShapeSaw,      0)
        self.PLFOShapeGrp.addButton(self.PLFOShapePulse,    1)
        self.PLFOShapeGrp.addButton(self.PLFOShapeTriangle, 2)
        self.PLFOShapeGrp.addButton(self.PLFOShapeNoise,    3)
        self.tabs = QtWidgets.QTabWidget()
        self.core   = QtWidgets.QWidget() 
        self.LFOTab = QtWidgets.QWidget() 
        self.LPFTab = QtWidgets.QWidget() 
        self.tabs.addTab(self.core, "Core")
        self.tabs.addTab(self.LFOTab, "LFO")
        self.tabs.addTab(self.LPFTab, "LPF")
        #self.tabs.setStyleSheet("QCheckBox { background-color: red }")
        #self.tabs.palette.setColor(QtGui.QPalette.window(), "{ color: red}")
        # LAYOUT
        hgrid = QtWidgets.QGridLayout(self)
        hgrid.setContentsMargins(0, 0, 0, 0)
        hgrid.addWidget(self.tabs,              5, 0, 7, 2)
        self.core.layout   = QtWidgets.QGridLayout(self.core)
        self.LFOTab.layout = QtWidgets.QGridLayout(self.LFOTab)
        self.LPFTab.layout = QtWidgets.QGridLayout(self.LPFTab)

        curLayout = self.core.layout
        curLayout.addWidget(self.SlotIsNoise,  0, 0, 1, 1)
        curLayout.addWidget(self.SlotIsON,     0, 1, 1, 1)
        curLayout.addWidget(self.SlotLoopON,   1, 0, 1, 1)
        curLayout.addWidget(self.DSPLabel,     2, 0, 1, 1)
        curLayout.addWidget(self.DACLabel,     2, 1, 1, 1)
        curLayout.addWidget(self.DSPLevel,     3, 0, 1, 1, QtCore.Qt.AlignCenter)
        curLayout.addWidget(self.DACLevel,     3, 1, 1, 1, QtCore.Qt.AlignCenter)
        curLayout.addWidget(self.DACPanSlider, 4, 1, 1, 1, QtCore.Qt.AlignCenter)
        
        curLayout = self.LFOTab.layout
        curLayout.addWidget(self.LFOReset,          0, 0, 1, 2, QtCore.Qt.AlignHCenter)
        curLayout.addWidget(self.LFOOscFreq,        1, 0, 1, 2)        
        curLayout.addWidget(self.ALFOLevel,         2, 0, 1, 1)
        curLayout.addWidget(self.PLFOLevel,         2, 1, 1, 1)
        curLayout.addWidget(self.ALFOShapeSaw,      3, 0, 1, 1)
        curLayout.addWidget(self.ALFOShapePulse,    4, 0, 1, 1)
        curLayout.addWidget(self.ALFOShapeTriangle, 5, 0, 1, 1)
        curLayout.addWidget(self.ALFOShapeNoise,    6, 0, 1, 1)
        curLayout.addWidget(self.PLFOShapeSaw,      3, 1, 1, 1)
        curLayout.addWidget(self.PLFOShapePulse,    4, 1, 1, 1)
        curLayout.addWidget(self.PLFOShapeTriangle, 5, 1, 1, 1)
        curLayout.addWidget(self.PLFOShapeNoise,    6, 1, 1, 1)
        
        curLayout = self.LPFTab.layout
        #TODO

        # ACTIONS
        self.SlotIsON.clicked.connect(self.changeOnOFF)
        self.SlotIsNoise.clicked.connect(self.changeNoiseOnOFF)
        self.SlotLoopON.clicked.connect(self.changeLoopOnOFF)
        #self.SlotSourceRangeSlider.valueChanged.connect(self.changeSourceRange)
        self.DACLevel.valueChanged.connect(self.changeVolume)
        self.DACPanSlider.valueChanged.connect(self.changePan)
        self.DSPLevel.valueChanged.connect(self.changeDSPVolume)

        self.LFOOscFreq.valueChanged.connect(self.setLFOFreq)
        self.LFOReset.clicked.connect(self.setLFOReset)
        self.ALFOLevel.valueChanged.connect(self.setALFOLevel)
        self.PLFOLevel.valueChanged.connect(self.setPLFOLevel)
        self.ALFOShapeGrp.buttonReleased.connect(self.setALFOShape)
        self.PLFOShapeGrp.buttonReleased.connect(self.setPLFOShape)

    def setLFOFreq(self):
        freq = self.LFOOscFreq.value()
        Slot_LFO_Osc_Freq(freq, self.myNode.slotNr)

    def setLFOReset(self):
        if self.LFOReset.checkState() == QtCore.Qt.Checked:
            Slot_LFO_Reset(1, self.myNode.slotNr)
        else:
            Slot_LFO_Reset(0, self.myNode.slotNr)

    def setALFOLevel(self):
        lvl = self.ALFOLevel.value()
        Slot_ALFO_Level(lvl, self.myNode.slotNr)

    def setPLFOLevel(self):
        lvl = self.PLFOLevel.value()
        Slot_PLFO_Level(lvl, self.myNode.slotNr)

    def setALFOShape(self):#TODO 
        shape = self.ALFOShapeGrp.checkedId()
        if shape != int(-1):
            Slot_ALFO_Shape(shape, self.myNode.slotNr)

    def setPLFOShape(self):
        shape = self.PLFOShapeGrp.checkedId()
        if shape != int(-1):
            Slot_PLFO_Shape(shape, self.myNode.slotNr)

    def setNode(self, node):
        self.myNode = node

    def changeOnOFF(self):
        if self.SlotIsON.checkState() == QtCore.Qt.Checked:
            Slot_enable(1, self.myNode.slotNr)
        else:
            Slot_enable(0, self.myNode.slotNr)

    def changeNoiseOnOFF(self):
        if self.SlotIsNoise.checkState() == QtCore.Qt.Checked:
            Slot_setNoise(1, self.myNode.slotNr)
            AICAUtils.setPortColorDisabled(self.myNode.input(0))
            AICAUtils.setPortColorEnabled(self.myNode.input(1))
        else:
            Slot_setNoise(0, self.myNode.slotNr)
            AICAUtils.setPortColorEnabled(self.myNode.input(0))
            AICAUtils.setPortColorDisabled(self.myNode.input(1))

    def changeLoopOnOFF(self):
        Slot_AttackRate(0x1F, self.myNode.slotNr) #TODO TEMP HERE
        if self.SlotLoopON.checkState() == QtCore.Qt.Checked:
            Slot_LoopEnable(1, self.myNode.slotNr)
        else:
            Slot_LoopEnable(0, self.myNode.slotNr)

    #def changeSourceRange(self):
    #    loopStart = self.SlotSourceRangeSlider.first.value()
    #    loopEnd   = self.SlotSourceRangeSlider.second.value()
    #    print ("SourceRange: start:", loopStart, ", end:", loopEnd)

    def changeVolume(self):
        vol = self.DACLevel.value()
        Slot_Volume(vol, self.myNode.slotNr)
        if vol > 0:
            AICAUtils.setPortColorEnabled(self.myNode.output(0))
        else:
            AICAUtils.setPortColorDisabled(self.myNode.output(0))

    def changePan(self):
        pan = self.DACPanSlider.value()
        Slot_Panning(pan, self.myNode.slotNr)

    def changeDSPVolume(self):
        vol = self.DSPLevel.value()
        Slot_DSPVolume(vol, self.myNode.slotNr)
        if vol > 0:
            AICAUtils.setPortColorEnabled(self.myNode.output(1))
        else:
            AICAUtils.setPortColorDisabled(self.myNode.output(1))

class SlotNodeWidgetWrapper(NodeBaseWidget):
    # Wrapper that allows the widget to be added in a node object.
    def __init__(self, parent=None):
        super(SlotNodeWidgetWrapper, self).__init__(parent)
        self.set_name('my_widget')
        #self.set_label('Custom Widget')
        self.myWidget = SlotCustomWidget()
        self.set_custom_widget(self.myWidget)

    def get_value(self):
        return 1
    
    def set_value(self, value):
        value = value + 1

    def setNode(self, node):
        self.myWidget.myNode = node

#TODO: set ATTACK RATE !!!!    0x1f;

#=======================
#LATER: ADD FEG Rate change, (ADSR) CUTOFF FREQ...    

#Time Variation Filter = FEG -> influences the LPF
#FAR, FD1R, FD2R, FRR = FEG attac/Decay1/decay2/Release
        #also, but via graph: connect to which DSP input

#LFOF frequency
#ALFOS -> degree of influence of LFO to EG (amplitude)
#PLFOS -> degree of influence of LFO to the pitch (frequency)

