# YAMAHA AICA
# ===========
# GD AUDIO -> TO DSP: pass-thru to DIGITAL MIXER, or used in DSP
# PCM (SOUND RAM) or NOISE: 64 SLOTS (CHANNELS) -> TO DSP or TO DIGITAL MIXER
#
# DSP: programmable effects
#
# DIGITAL MIXER
#
# DAC

#from Qt import QtWidgets          https://doc.qt.io/qt-6/gallery.html
from NodeGraphQt import NodeGraph

from aica_prot   import * # Protocol to exchange data with the Dreamcast
from aica_gdrom  import *
from aica_source import *
from aica_slot   import *
from aica_dsp    import *
from aica_mixer  import * 
from aica_dac    import * 

#import time
#import rtmidi #pip install python-rtmidi
#from rtmidi.midiutil import open_midiinput

# test function.
def src_add():
    srcNode = graph.create_node('audio.source.AudioSourceNode', name="AUDIO_SOURCE")
    srcNode.loadFile()
def slot_add(graph):
    node_slots.add(node_mx_slots)
    node_slots.autoWrap()
def slot_remove(graph):
    node_slots.remove(node_mx_slots)
    node_slots.autoWrap()
def mixs_add(graph):
    node_dsp_mixs.add()
def mixs_remove(graph):
    node_dsp_mixs.remove()

def readMidiMessages(msg, data):
    message, deltatime = msg
    match message[0]:
        case 128: # 0x80 (to 0x8F)
            Slot_Midi_Note_Off(message[1], 0) # 3rd byte is velocity
        case 144: # 0x90 (to 0x9F)
            Slot_Midi_Note_On(message[1], 0) # 3rd byte is velocity
        case 176: # 0xB0 (to 0xBF) + 2nd=1 for modulation wheel
            print("MIDI Mod:", message)
            # 2nd byte = 0 -> 15 = Arturia Keystep37 CC bancks (b1-b4)x4 knobs -> b1-knob2 overlaps with mod wheel
        case 224: # 0xE0 (to 0xEF) + byte2 & 3 = 0-127 LSB and MSB
            print("MIDI Pitch:", message)
        case _:
            print("MIDI not supported:", message)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    # create node graph controller
    graph = NodeGraph()
    
    # customize the context menu
    menu  = graph.get_context_menu('graph')
    menu.add_command('Add Audio Source...', src_add)
    #TODO: add Sine Wave..., Add Square Wave..., Add Triangle Wave.... L-SAW, R-SAW
    menu.add_separator()
    menu.add_command('Add Slot', slot_add)
    menu.add_command('Remove Slot', slot_remove)
    menu.add_separator()
    menu.add_command('Add DSP Input', mixs_add)
    menu.add_command('Remove DSP Input', mixs_remove)

    # register the node classes
    graph.register_node(AudioSourceNode)
    graph.register_node(GDRomNode)
    graph.register_node(SlotsNode)
    graph.register_node(SlotNode)
    graph.register_node(DSPNode)
    graph.register_node(DSPSlotsInputsNode)
    graph.register_node(DSPExternalInputsNode)
    graph.register_node(DigitalMixerNode)
    graph.register_node(DSPEffectsInputsNode)
    graph.register_node(DSPDigitalAudioInputsNode)
    graph.register_node(SlotsInputsNode)
    graph.register_node(DACNode)

    # show the node graph widget
    graph_widget = graph.widget
    graph_widget.show()

    # Audio Sources
    node_slots  = graph.create_node('aica.slots.SlotsNode', name='AICA SLOTS (Max 64)')
    node_slots.set_pos(0, 0)
    node_slots.set_size(200, 600)

    node_gdrom = graph.create_node('gdrom.GDRomNode', name='GD-ROM Audio')
    node_gdrom.set_pos(0, 650)

    # DSP
    node_dsp = graph.create_node('aica.dsp.DSPNode', name='AICA DSP')
    node_dsp.set_pos(300, 400)
    node_dsp.set_size(250, 350)
    node_dsp_mixs = graph.create_node('aica.dsp.DSPSlotsInputsNode', name='Inputs from Slots (Max: 16)')
    node_dsp_mixs.set_pos(310, 430)
    #node_dsp.set_size(50, 50)
    node_dsp_exts = graph.create_node('aica.dsp.DSPExternalInputsNode', name='GD-ROM Audio Inputs')
    node_dsp_exts.set_pos(310, 490)
    #node_dsp.set_size(50, 50)

    # Mixer
    node_mx_ = graph.create_node('aica.DigitalMixerNode', name='AICA Digital Mixer')
    node_mx_.set_pos(550, 0)
    node_mx_.set_size(400, 750)
    node_mx_slots = graph.create_node('aica.mixer.SlotsInputsNode', name='Inputs from Slots (Max:64)')
    node_mx_slots.set_pos(560, 30)
    node_mx_dsp = graph.create_node('aica.mixer.DSPEffectsInputsNode', name='Inputs from DSP Effects (Max:16)')
    node_mx_dsp.set_pos(560, 375)
    node_mx_da = graph.create_node('aica.mixer.DSPDigitalAudioInputsNode', name='Inputs from DSP Digital Audio')
    node_mx_da.set_pos(560, 650)
    
    # DAC
    node_dac = graph.create_node('aica.dac.DACNode', name='AICA DAC')
    node_dac.set_pos(1000, 375)

    # Link Mixer -> DAC
    node_mx_slots.link2DAC()
    node_mx_dsp.link2DAC()
    node_mx_da.link2DAC()

    # adding 1 slot as a start
    slot_add(graph)

    node_gdrom.set_output(0, node_dsp_exts.input(0))
    node_gdrom.set_output(1, node_dsp_exts.input(1))
    node_dsp_exts.set_output(0, node_mx_da.input(0))
    node_dsp_exts.set_output(1, node_mx_da.input(1))

    createNamedPipe(myPipePath)
      

    #midiin = rtmidi.MidiIn()
    #available_ports = midiin.get_ports()
    #print (available_ports)
    #try:
    #    midiin, port_name = open_midiinput(1)
    #except (EOFError, KeyboardInterrupt):
    #    exit()
    #midiin.set_callback(readMidiMessages, None)

    app.exec_()

    print("Exiting...")
    #midiin.close_port()
    #del midiin


#TODO: midi selector: do not hang the app if not selected -> add in node ?
#TODO: OSC/voice select
#TODO: Timbrality select   -> create 1 new node: a) Osc/voice, b) num tones, c) polyphony, d) note priority, e) split kbd

#TODO: own wav reader

#TODO: LFO settings cleanup
#TODO: LPF settings
#TODO: EG graph: amplitude envelope: graph ?  MID-HI
#TODO: FEG graph

#---------------
#TODO: handle upload of multiple wav files (RAM Mgmt)
#TODO: compile common, slots, DSP, mixer, ARM states into a file format ?
#TODO: save graph setup into file

#TODO: send initial config of AICA: DAC & slots. also arm reset ?

#TODO: add Sine Wave..., Add Square Wave..., Add Triangle Wave.... L-SAW, R-SAW

# TODO: AICA_SLOT_PITCH_FNUMBER & AICA_SLOT_OCTAVE: controlled by midi keyboard   EAZY 
#TODO: key on/off all: replace with button ? -> also controlled by midi keyboard ?  EAZY

#========================================================
# - LPF with cutoff freq that can be varied over time

#Select: Osc per Voice -> eg 2 -> Polyphony = 32
#Select: Timbrality    -> eg 2 -> Polyphony = 16
#                            4                 8
#new node: Tone -> contains X osc (slots), with "detune" between slots

