# YAMAHA AICA DAC
# ===============

from Qt import QtWidgets, QtCore

from NodeGraphQt import BaseNode, NodeBaseWidget
import posix

from aica_prot   import *
from aica_utils  import *
#######################################################
# 
#######################################################
class DACNode(BaseNode):
    __identifier__ = 'aica.dac'
    NODE_NAME = 'AICA DAC Node'

    def __init__(self):
        super(DACNode, self).__init__()

        # create the output ports
        self.add_input('LEFT', multi_input=True) 
        self.add_input('RIGHT', multi_input=True) 

        # create the output ports
        self.add_output('OUT_L')
        self.add_output('OUT_R')

        # custom widgets
        self.node_widget = DACNodeWidgetWrapper(self.view)
        self.node_widget.setNode(self)
        self.add_custom_widget(self.node_widget, tab='Custom')

class DACNodeWidget(QtWidgets.QWidget):
    # Custom widget to be embedded inside a SlotNode.
    def __init__(self, parent=None):
        super(DACNodeWidget, self).__init__(parent)
        # UI ELEMENTS
        self.DACIsMono = QtWidgets.QCheckBox("Mono")
        self.DACIsMono.setStyleSheet("QCheckBox { color: white }")
        #self.DACIsON = QtWidgets.QCheckBox("ON")
        #self.DACIsON.setStyleSheet("QCheckBox { color: white }")
        self.DACIsON      = QtWidgets.QPushButton("ON")
        self.DACMasterVolDial = QtWidgets.QDial()
        self.DACMasterVolDial.setRange(0,15)
        self.DACMasterVolDial.setTracking(0)
        # LAYOUT
        hgrid = QtWidgets.QGridLayout(self)
        hgrid.setContentsMargins(0, 0, 0, 0)
        hgrid.addWidget(self.DACIsMono,        0, 0, 1, 1)
        hgrid.addWidget(self.DACIsON,          0, 1, 1, 1)
        hgrid.addWidget(self.DACMasterVolDial, 1, 0, -1, -1, QtCore.Qt.AlignCenter )
        # ACTIONS
        self.DACIsON.clicked.connect(self.changeOnOFF)
        self.DACIsMono.clicked.connect(self.changeMonoStereo)
        self.DACMasterVolDial.valueChanged.connect(self.changeVolume)

    def changeOnOFF(self):
        #if self.DACIsON.checkState() == QtCore.Qt.Checked:
        DAC_enable(1)
        #else:
        #    DAC_enable(0)  #there is no "DAC OFFF"
        self.setOutputPortColors()

    def changeMonoStereo(self):
        if self.DACIsMono.checkState() == QtCore.Qt.Checked:
            DAC_Mono(1)
        else:
            DAC_Mono(0)

    def changeVolume(self):
        vol = self.DACMasterVolDial.value()
        DAC_Volume(vol)
        self.setOutputPortColors()

    def setOutputPortColors(self):
        vol = self.DACMasterVolDial.value()
        if (vol > 0) : #and (self.DACIsON.checkState() == QtCore.Qt.Checked)
            AICAUtils.setPortColorEnabled(self.myNode.output(0))
            AICAUtils.setPortColorEnabled(self.myNode.output(1))
        else:
            AICAUtils.setPortColorDisabled(self.myNode.output(0))
            AICAUtils.setPortColorDisabled(self.myNode.output(1))

class DACNodeWidgetWrapper(NodeBaseWidget):
    # Wrapper that allows the widget to be added in a node object.
    def __init__(self, parent=None):
        super(DACNodeWidgetWrapper, self).__init__(parent)
        self.set_name('my_widget')
        #self.set_label('Custom Widget')
        self.myWidget = DACNodeWidget()
        self.set_custom_widget(self.myWidget)

    def get_value(self):
        return 1
    
    def set_value(self, value):
        value = value + 1

    def setNode(self, node):
        self.myWidget.myNode = node