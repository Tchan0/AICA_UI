# Audio Source for the YAMAHA AICA
# ================================
# Possible formats:
# - 8bit or 16bit raw audio (PCM)
# - 4bit Yamaha ADPCM

from Qt import QtCore, QtWidgets
from NodeGraphQt import BaseNode, NodeBaseWidget

import os
import soundfile as sf   # pip install soundfile
                         # pip install numpy         (soundfile dependency)
#import numpy as np
#######################################################
# Individual Source = Audio file
#######################################################
class AudioSourceNode(BaseNode):
    __identifier__ = 'audio.source'
    NODE_NAME = 'Audio Source Node'

    def __init__(self):
        super(AudioSourceNode, self).__init__()
        self.set_port_deletion_allowed(True)
        self.resetProps()
        # custom widgets
        self.node_widget = AudioSourceNodeWidgetWrapper(self.view)
        self.node_widget.setNode(self)
        self.add_custom_widget(self.node_widget, tab='Custom')

    # create the output ports
    def addOutputPorts(self, numChannels):
        outDic = self.outputs()
        for x in outDic:
            self.delete_output(x)

        if numChannels == 2:
            self.add_output('LEFT')
            self.add_output('RIGHT')
        else:
            self.add_output('MONO')

    def resetProps(self):
        self.set_name("NOT_LOADED")
        self.bits                 = 0
        self.numChannels          = 0
        self.samplerate           = 0
        self.numSamplesPerChannel = 0
        if hasattr(self, 'node_widget') and hasattr(self.node_widget, 'myWidget'):
            self.node_widget.myWidget.changeTexts()

    def loadFile(self):
        self.resetProps()

        filesList = QtWidgets.QFileDialog.getOpenFileName(None, "Open Audio file", QtCore.QDir.currentPath(),"Audio files (*.wav *.pcm *.raw);;All files (*.*)","", QtWidgets.QFileDialog.DontUseNativeDialog)
        if len(filesList[0]) == 0:
            print ("NO FILE LOADED")
            return

        print ("Trying to load:", str(filesList[0]))
        tryAlternative = 0
        isRAWfile = 0
        try: # Yamaha ADPCM WAV files are not recognized by soundfile
            data, self.samplerate = sf.read(filesList[0], dtype='int16') #TODO: replace soundfile. Cannot import int8, SUCKKKEEERRRRRRRRR !!
        except sf.LibsndfileError as e:
            print("INFO: WAV format not supported by Soundfile lib, trying with internal code...")
            tryAlternative = 1
        except TypeError as e:
            isRAWfile = 1            

        if tryAlternative:
            print ("hello Yamaha ADPCM...(TODO)")
            return
        elif isRAWfile:
            print ("please specify bits/rate/channels...(TODO)")
            #display dialog
            #sf.read(filesList[0], channels=1, samplerate=44100,subtype='PCM_S8')
            return

        file_stats = os.stat(filesList[0])
        self.audioData            = data
        self.bits                 = AudioSourceNode.guessBitsPrecision(file_stats.st_size, data.size)
        self.numChannels          = data.ndim
        #self.samplerate          = already set above
        self.numSamplesPerChannel = len(data)

        
        print ("BitPrecision:", self.bits)
        print ("Num Channels:", self.numChannels)
        print ("Sample Rate:", self.samplerate)
        print ("Samples per Channel:", self.numSamplesPerChannel)

        self.node_widget.myWidget.changeTexts()

        # Filename -> Node Title
        head_tail = os.path.split(filesList[0])
        #print ("path is:", head_tail[0])
        #print ("filename is:", head_tail[1])
        self.set_name(name=head_tail[1])

        # Mono/Stereo
        self.addOutputPorts(self.numChannels)
        

    #soundfile seems to convert our data to float64, and I can't seem to find info on the original bits, so I'm doing a hacky/educated guess... 
    def guessBitsPrecision(filesize, totalNumSamples):
        if ( (totalNumSamples * 2) + 44 > filesize):
            return 8
        else:
            return 16

class AudioSourceCustomWidget(QtWidgets.QWidget):
    # Custom widget to be embedded inside a SlotNode.
    def __init__(self, parent=None):
        super(AudioSourceCustomWidget, self).__init__(parent)
        # UI ELEMENTS
        self.BitsLabel       = QtWidgets.QLabel()
        self.RateLabel       = QtWidgets.QLabel()
        self.NumSamplesLabel = QtWidgets.QLabel()
        #self.SecsLabel       = QtWidgets.QLabel()
        #self.KBytesLabel     = QtWidgets.QLabel()
        self.LoadButton      = QtWidgets.QPushButton("Load...")
        # LAYOUT
        hgrid = QtWidgets.QGridLayout(self)
        hgrid.setContentsMargins(0, 0, 0, 0)
        hgrid.addWidget(self.BitsLabel,       0, 0, 1, 1)
        hgrid.addWidget(self.RateLabel,       0, 1, 1, 1)
        hgrid.addWidget(self.NumSamplesLabel, 1, 0, 1, -1, QtCore.Qt.AlignCenter)
        #hgrid.addWidget(self.SecsLabel,       2, 0, 1, -1, QtCore.Qt.AlignCenter)
        #hgrid.addWidget(self.KBytesLabel,     3, 0, 1, -1, QtCore.Qt.AlignCenter)
        hgrid.addWidget(self.LoadButton,      2, 0, 1, -1, QtCore.Qt.AlignCenter)

        # ACTIONS
        self.LoadButton.clicked.connect(self.loadFile)

    def setNode(self, node):
        self.myNode = node
        self.changeTexts()

    def loadFile(self):
        self.myNode.loadFile()

    def changeTexts(self):
        self.BitsLabel.setText("<font color=white>" + str(self.myNode.bits) + " bits</font>")
        self.RateLabel.setText("<font color=white>" + str(self.myNode.samplerate) + "</font>")
        self.NumSamplesLabel.setText("<font color=white>" + str(self.myNode.numSamplesPerChannel) + " smp/chn</font>")
        #self.SecsLabel.setText("<font color=white>1 sec</font>")
        #self.KBytesLabel.setText("<font color=white>15 KBytes</font>")

class AudioSourceNodeWidgetWrapper(NodeBaseWidget):
    # Wrapper that allows the widget to be added in a node object.
    def __init__(self, parent=None):
        super(AudioSourceNodeWidgetWrapper, self).__init__(parent)
        self.set_name('my_widget')
        #self.set_label('Custom Widget')
        self.myWidget = AudioSourceCustomWidget()
        self.set_custom_widget(self.myWidget)

    def get_value(self):
        return 1
    
    def set_value(self, value):
        value = value + 1

    def setNode(self, node):
        self.myWidget.setNode(node)
