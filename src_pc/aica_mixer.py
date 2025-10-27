# YAMAHA AICA DIGITAL MIXER
# =========================
# Inputs:
#   - DSP_OUT_1  (0x00802000) TO DSP_OUT_16 (0x0080203C): 16 x 16 bytes with EFSDL & EFPAN  (aka EFREG (Effect Register) output of DSP)
#   - DSP_OUT_17 (0x00802040): Digital audio 1L (EXTS, aka External Stack)
#   - DSP_OUT_18 (0x00802044): Digital audio 1R (EXTS, aka External Stack)
#   - SLOT_0 TO SLOT_63: 64 channels of sound slots (channel) direct data: with DISDL & DIPAN
#
# Output: L & R
#   - influenced by MASTER VOLUME (MVOL)
#   - sent to DAC

#from Qt import QtWidgets
from NodeGraphQt import BackdropNode, BaseNode
from NodeGraphQt.constants import PortTypeEnum

#######################################################
# Create a backdrop node to regroup all AICA Mixer nodes
#######################################################
class DigitalMixerNode(BackdropNode):
    __identifier__ = 'aica'
    NODE_NAME = 'AICA Digital Mixer Node'

    def __init__(self):
        super(DigitalMixerNode, self).__init__()

#######################################################
# 
#######################################################
class SlotsInputsNode(BaseNode):
    __identifier__ = 'aica.mixer'
    NODE_NAME = 'Slots Inputs Node'

    def __init__(self):
        super(SlotsInputsNode, self).__init__()
        self.set_port_deletion_allowed(mode=True)
        self._active_slots = 0
        # add the inputs from the slots
        #for x in range(1): #goes up to 63
        #    self.addSlotInputPort (x)
        # create the output ports
        self.add_output('LEFT') 
        self.add_output('RIGHT') 


    def getSlotName(self, slotnr):
        return 'SLOT_' + str(slotnr)

    def add(self):
        if self._active_slots < 64:
            rawPort = self.add_input(self.getSlotName(self._active_slots), color=(180, 80, 0))
            self.add_accept_port_type(rawPort, {'port_name': 'to_mixer',  'port_type': PortTypeEnum.OUT.value, 'node_type': 'aica.slots.SlotNode'})
            self._active_slots += 1

    def remove(self): #remove a slot
        if self._active_slots > 0:
            self.delete_input(self.getSlotName(self._active_slots - 1))
            self._active_slots -= 1

    def link2DAC(self):
        DACNodes = self.graph.get_nodes_by_type('aica.dac.DACNode')
        self.set_output(0, DACNodes[0].input(0))
        self.set_output(1, DACNodes[0].input(1))

#######################################################
# 
#######################################################
class DSPEffectsInputsNode(BaseNode):
    __identifier__ = 'aica.mixer'
    NODE_NAME = 'DSP Effects Inputs Node'

    def __init__(self):
        super(DSPEffectsInputsNode, self).__init__()
        # add the inputs from the DSP
        #for x in range(1):
            #self.addDSPInputPort (x)
        # create the output ports
        self.add_output('LEFT') 
        self.add_output('RIGHT') 

    def addDSPInputPort(self, portnr):
        self.add_input('DSP_OUT_' + str(portnr), color=(180, 80, 0))

    def link2DAC(self):
        DACNodes = self.graph.get_nodes_by_type('aica.dac.DACNode')
        self.set_output(0, DACNodes[0].input(0))
        self.set_output(1, DACNodes[0].input(1))

#######################################################
# 
#######################################################
class DSPDigitalAudioInputsNode(BaseNode):
    __identifier__ = 'aica.mixer'
    NODE_NAME = 'DSP Digital Audio Inputs Node'

    def __init__(self):
        super(DSPDigitalAudioInputsNode, self).__init__()
        # add the inputs from the Digital Audio
        rawPort = self.add_input('DSP_OUT_17', color=(180, 80, 0))
        self.add_accept_port_type(rawPort, {'port_name': 'EXTS_L',  'port_type': PortTypeEnum.OUT.value, 'node_type': 'aica.dsp.DSPExternalInputsNode'})
        rawPort = self.add_input('DSP_OUT_18', color=(180, 80, 0))
        self.add_accept_port_type(rawPort, {'port_name': 'EXTS_R',  'port_type': PortTypeEnum.OUT.value, 'node_type': 'aica.dsp.DSPExternalInputsNode'})

        # create the output ports
        self.add_output('LEFT') 
        self.add_output('RIGHT') 

    def link2DAC(self):
        DACNodes = self.graph.get_nodes_by_type('aica.dac.DACNode')
        self.set_output(0, DACNodes[0].input(0))
        self.set_output(1, DACNodes[0].input(1))

#===============================
#LATER: ? Ring Buffer
#LATER: ARMRST
#LATER LATER: MIDI, Monitoring, DMA, Timers, Interrupts