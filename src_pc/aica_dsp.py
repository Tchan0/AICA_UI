# YAMAHA AICA DSP
# ===============
# Inputs:
#   - MIXS: 16 slots (channels) coming from the Aica slots. (aka "Mix Stack")
#           Several Aica slots can point to 1 MIXS channel, the data is just summed up (! no overflow protection !)
#   - EXTS: 2 channels coming from Digital Audio (GD-ROM)
#   - ???MEMS = , aka Memory Stack = DSPs internal buffer
#
# Output:
#   - EFREG (16 slots (channels)) (volume level: EFSDL, panning: EFPAN)
#   - EXTS pass-thru


#from Qt import QtWidgets
from NodeGraphQt import BackdropNode, BaseNode
from NodeGraphQt.constants import PortTypeEnum

#######################################################
# Create a backdrop node to regroup all AICA DSP nodes
#######################################################
class DSPNode(BackdropNode):
    __identifier__ = 'aica.dsp'
    NODE_NAME = 'AICA DSP Node'

    def __init__(self):
        super(DSPNode, self).__init__()

#######################################################
# DSP Inputs from Aica Slots (MIXS)
#######################################################
class DSPSlotsInputsNode(BaseNode):
    __identifier__ = 'aica.dsp'
    NODE_NAME = 'AICA DSP Slots Inputs Node'

    def __init__(self):
        super(DSPSlotsInputsNode, self).__init__()
        self.set_port_deletion_allowed(mode=True)
        self._active_slots = 0

    def getSlotName(self, slotnr):
        return 'MIXS_' + str(slotnr)

    def add(self): #add a slot
        if self._active_slots < 16:
            mixsPort = self.add_input(self.getSlotName(self._active_slots), color=(180, 80, 0), multi_input=True)
            self.add_accept_port_type(mixsPort, {'port_name': 'to_DSP', 'port_type': PortTypeEnum.OUT.value, 'node_type': 'aica.slots.SlotNode'})
            self._active_slots += 1

    def remove(self): #remove a slot
        if self._active_slots > 0:
            self.delete_input(self.getSlotName(self._active_slots - 1))
            self._active_slots -= 1

        # create the output ports
        #self.add_output('to_mixer')
        #self.add_output('to_DSP')   

#######################################################
# DSP Inputs from Digital Audio (EXTS)
#######################################################
class DSPExternalInputsNode(BaseNode):
    __identifier__ = 'aica.dsp'
    NODE_NAME = 'AICA DSP External Inputs Node'

    def __init__(self):
        super(DSPExternalInputsNode, self).__init__()

        # add the inputs ports
        rawPort = self.add_input('EXTS_L')
        self.add_accept_port_type(rawPort, {'port_name': 'LEFT',  'port_type': PortTypeEnum.OUT.value, 'node_type': 'gdrom.GDRomNode'})
        rawPort = self.add_input('EXTS_R')
        self.add_accept_port_type(rawPort, {'port_name': 'RIGHT',  'port_type': PortTypeEnum.OUT.value, 'node_type': 'gdrom.GDRomNode'})

        # create the output ports
        self.add_output('EXTS_L')
        self.add_output('EXTS_R')

# TODO: DSP: everything

#Theory
# The long buffer is a sequence of data, which stores the original signal after it is processed in some time around 500ms
# Block processing corresponds to a signal processing in which the signal is processed not in a sample by sample basis, but by bigger blocks of n samples, where n is the block length.

# Simples effect = delay = delay + gain (factor)
#   special delays: https://www.youtube.com/shorts/U_zGNzam4y4

# REverb vs delay: https://www.youtube.com/watch?v=SCUUu96PYjo

#room space = reverb, or R+D ?   reverb adds space, delay adds depth. 

#reverb + delay

# Example effects
#Delay
#chorus  https://www.youtube.com/watch?v=4vRleMQdZZU   https://www.youtube.com/watch?v=zmN7fK3fKUE
#flanger https://www.youtube.com/watch?v=4vRleMQdZZU
#phaser  https://www.youtube.com/watch?v=4vRleMQdZZU
#Reverb E M S
#Qsound4
#Qsound8
