#http://midi.teragonaudio.com/tech/midispec.htm
#https://fmslogo.sourceforge.io/manual/midi-table.html

import time
import rtmidi #pip install python-rtmidi
from rtmidi.midiutil import open_midiinput

    midiin = rtmidi.MidiIn()
    available_ports = midiin.get_ports()
    print (available_ports)
    try:
        midiin, port_name = open_midiinput(1)
    except (EOFError, KeyboardInterrupt):
        exit()
    midiin.set_callback(readMidiMessages, None)



    midiin.close_port()
    del midiin

def readMidiMessages(msg, data):
    message, deltatime = msg
    match message[0]:
        case 128: # 0x80 (to 0x8F)
            Slot_Midi_Note_Off(message[1], 0) # 3rd byte is velocity
        case 144: # 0x90 (to 0x9F)
            Slot_Midi_Note_On(message[1], 0) # 3rd byte is velocity
        case 176: # 0xB0 (to 0xBF) + 2nd=1 for modulation wheel
            print("MIDI Mod:", message)
        case 224: # 0xE0 (to 0xEF) + byte2 & 3 = 0-127 LSB and MSB
            print("MIDI Pitch:", message)
        case _:
            print("MIDI not supported:", message)