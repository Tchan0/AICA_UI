# Protocol to exchange data with the Dreamcast

# Pipe Files on Linux
# https://stackoverflow.com/questions/1430446/create-a-temporary-fifo-named-pipe-in-python
# These kind of files only stores what have been written but not read, so implementing a circular buffer may not be necessary.
# mkfifo https://askubuntu.com/questions/449132/why-use-a-named-pipe-instead-of-a-file
# https://discord.com/channels/488332893324836864/488332893324836866/1176634666703396925
# https://www.linuxjournal.com/article/2156
# https://github.com/spencerelliott/dEngine/blob/dreamcast-pvr/src/devtools.c
# https://discord.com/channels/488332893324836864/488332893324836866/1177008401205698601

import os, stat
import posix

AICA_RAM_START = 0x00800000
AICA_RAM_MAX   = 0x009FFFFF   # 2 MB RAM AICA (DREAMCAST, ATOMISWAVE)
#AICA_RAM_MAX   = 0x00FFFFFF   # 8 MB RAM AICA (NAOMI 1/2, SYSTEM SP, HIKARU)

myPipePath = "./bin/tmpUIXCHG.bin"
pipe = 0

#Delete pipe file
def deleteNamedPipe(pipePath):
    try:
        os.remove(pipePath) 
        print(f"Named pipe removed from: {pipePath}")
    except OSError as e:
        print(f"Error: {e}")

#Named pipe creation
def createNamedPipe(pipePath):
    #bPipeFileExists = stat.S_ISFIFO(os.stat(pipePath).st_mode)
    try:
        #if (bPipeFileExists):
            #deleteNamedPipe(pipePath)
        os.mkfifo(pipePath) 
        print(f"Named pipe created at: {pipePath}")
        global pipe
        pipe = posix.open(myPipePath, posix.O_RDWR)
    except OSError as e:
        print(f"Error: {e}")

    #pipe = posix.open(myPath, posix.O_RDWR)
    #pipe = posix.open("zztest.bin", posix.O_RDWR | posix.O_CREAT)
    #posix.write(pipe, b"Hello, named pipe!\n")


# 1st byte = Command, [optional: more bytes]
CMD_DAC_ENABLE      = 0x01
CMD_DAC_DISABLE     = 0x02 #TODO REMOVE THIS, DOES NOT EXIST
CMD_DAC_MONO        = 0x03
CMD_DAC_STEREO      = 0x04
CMD_DAC_VOLUME      = 0x05

CMD_SLOT_ENABLE     = 0x06
CMD_SLOT_DISABLE    = 0x07
CMD_SLOT_ISNOISE    = 0x08
CMD_SLOT_ISSOUND    = 0x09
CMD_SLOT_VOLUME     = 0x0A
CMD_SLOT_PANNING    = 0x0B
CMD_SLOT_LOOP_ON    = 0x0C
CMD_SLOT_LOOP_OFF   = 0x0D
CMD_SLOT_LOOP_START = 0x0E
CMD_SLOT_LOOP_END   = 0x0F
CMD_SLOT_ATTACK     = 0x10
CMD_SLOT_DECAY1     = 0x11
CMD_SLOT_DECAY2     = 0x12
CMD_SLOT_RELEASE    = 0x13
CMD_SLOT_FORMAT     = 0x14
CMD_SLOT_RAMPTR     = 0x15

CMD_SLOT_LFO_OSC_FREQ    = 0x20
CMD_SLOT_LFO_RESET       = 0x21
CMD_SLOT_ALFO_SHAPE      = 0x22
CMD_SLOT_ALFO_LEVEL      = 0x23
CMD_SLOT_PLFO_SHAPE      = 0x24
CMD_SLOT_PLFO_LEVEL      = 0x25

CMD_SLOT_MIDI_NOTE_ON    = 0x30
CMD_SLOT_MIDI_NOTE_OFF   = 0x31

CMD_LOAD_WAVEDATA   = 0x50

CMD_SLOT_DSPVOLUME  = 0x60 #TEMP ID

#TODO: add control the ARMRST ?

def DAC_enable(bEnable):
    outBA = bytearray()
    if bEnable:
        outBA.append(CMD_DAC_ENABLE)
        print ("enable DAC")
    else:
        outBA.append(CMD_DAC_DISABLE)
        print ("disable DAC")
    posix.write(pipe, outBA)
    
def DAC_Mono(isMono):
    outBA = bytearray()
    if isMono:
        outBA.append(CMD_DAC_MONO)
        print ("DAC: Mono")
    else:
        outBA.append(CMD_DAC_STEREO)
        print ("DAC: Stereo")
    posix.write(pipe, outBA)

def DAC_Volume(volume):
    outBA = bytearray()
    outBA.append(CMD_DAC_VOLUME)
    if volume > 15:
        volume = 15
    print ("DAC volume:", volume)
    outBA.append(volume)
    posix.write(pipe, outBA)

def Slot_enable(bEnable, slotNr):
    if slotNr > 63:
        return
    outBA = bytearray()
    if bEnable:
        outBA.append(CMD_SLOT_ENABLE)
        print ("SLOT", slotNr, ": ENABLE")
    else:
        outBA.append(CMD_SLOT_DISABLE)
        print ("SLOT", slotNr, ": DISABLE")
    outBA.append(slotNr)
    posix.write(pipe, outBA)

def Slot_setNoise(bEnable, slotNr):
    if slotNr > 63:
        return
    outBA = bytearray()
    if bEnable:
        outBA.append(CMD_SLOT_ISNOISE)
        print ("SLOT", slotNr, ": is NOISE")
    else:
        outBA.append(CMD_SLOT_ISSOUND)
        print ("SLOT", slotNr, ": is SOUND")
    outBA.append(slotNr)
    posix.write(pipe, outBA)

def Slot_Volume(volume, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_VOLUME)
    if volume > 15:
        volume = 15
    print ("SLOT", slotNr, "TO DAC volume:", volume)
    outBA.append(slotNr)
    outBA.append(volume)
    posix.write(pipe, outBA)

def Slot_Panning(panning, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_PANNING)
    if panning < 0:                                        #Left_MAX       center        RIGHT_MAX
        panning = panning * -1                             #0x1F            0x00          0x0F        AICA
        panning += 16                                      # -15               0           15         Qt
    print ("SLOT", slotNr, "pan:", panning)
    outBA.append(slotNr)
    outBA.append(panning)
    posix.write(pipe, outBA)

def Slot_LoopEnable(bEnable, slotNr):
    if slotNr > 63:
        return
    outBA = bytearray()
    if bEnable:
        outBA.append(CMD_SLOT_LOOP_ON)
        print ("SLOT", slotNr, ": LOOP ON")
    else:
        outBA.append(CMD_SLOT_LOOP_OFF)
        print ("SLOT", slotNr, ": LOOP OFF")
    outBA.append(slotNr)
    posix.write(pipe, outBA)

def Slot_LoopSetStart(start, slotNr):
    if slotNr > 63:
        return
    if start > 65534: #0xFFFF: 
        start = 65534 #0xFFFF
    outBA = bytearray()
    outBA.append(CMD_SLOT_LOOP_START)
    print ("SLOT", slotNr, ": SET START: ", start)
    outBA.append(slotNr)
    outBA.extend(start.to_bytes(length=2, byteorder='little'))
    #outBA.append(start & 0xFF)    
    #outBA.append((start >> 8) & 0xFF)
    posix.write(pipe, outBA)

def Slot_LoopSetEnd(end, slotNr):
    if slotNr > 63:
        return
    if end > 65534: # 0xFFFF:
        end = 65534 # 0xFFFF
    outBA = bytearray()
    outBA.append(CMD_SLOT_LOOP_END)
    print ("SLOT", slotNr, ": SET END: ", end )
    outBA.append(slotNr)
    outBA.extend(end.to_bytes(length=2, byteorder='little'))
    #outBA.append(end  & 0xFF)
    #outBA.append((end  >> 8) & 0xFF)
    posix.write(pipe, outBA)

def Slot_DSPVolume(volume, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_DSPVOLUME)
    if volume > 15:
        volume = 15
    print ("SLOT", slotNr, "TO DSP volume:", volume)
    outBA.append(slotNr)
    outBA.append(volume)
    posix.write(pipe, outBA)

def Slot_AttackRate(attack, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_ATTACK)
    if attack > 0x1F:
        attack = 0x1F
    print ("SLOT", slotNr, "ATTACK:", attack)
    outBA.append(slotNr)
    outBA.append(attack)
    posix.write(pipe, outBA)

#TODO CMD_SLOT_DECAY1     = 0x11
#TODO CMD_SLOT_DECAY2     = 0x12
#TODO CMD_SLOT_RELEASE    = 0x13

def Slot_Format(numBits, isADPCM, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_FORMAT)
    if numBits > 8:
        format = 0    #0=16bit PCM
    elif numBits > 4:
        format = 1    #1=8bit PCM
    #TODO: isADPCM
    print ("SLOT", slotNr, "Format:", format)
    outBA.append(slotNr)
    outBA.append(format)
    posix.write(pipe, outBA)

def Slot_SetRamPtr(addr,slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_RAMPTR)
    outBA.append(slotNr)
    if (addr < AICA_RAM_START) or (addr >= AICA_RAM_MAX): #ptr to AICA RAM address
        return
    outBA.extend(addr.to_bytes(length=4, byteorder='little'))
    posix.write(pipe, outBA)

def Slot_SetWaveDataPtrs(addr,startSample,endSample,slotNr):
    Slot_SetRamPtr(addr, slotNr)
    Slot_LoopSetStart(startSample, slotNr)
    Slot_LoopSetEnd(endSample, slotNr)

def Aica_LoadWaveData(addr,siz,bytes):
    print ("LoadWaveData addr:", addr, "siz:", siz)
    outBA = bytearray()
    outBA.append(CMD_LOAD_WAVEDATA)
    if (addr < AICA_RAM_START) or (addr >= AICA_RAM_MAX): #ptr to AICA RAM address
        return
    outBA.extend(addr.to_bytes(length=4, byteorder='little'))
    if (siz > 0x00180000):                         #size of wave data following  TODO: arbitrary limit - correct/remove this
        siz = 0x00180000
    outBA.extend(siz.to_bytes(length=4, byteorder='little'))
    outBA.extend(bytes[:siz]) # [:siz]  xxx bytes: wave data
    print ("Length of outBA:", len(outBA))
    posix.write(pipe, outBA)

def Slot_LFO_Osc_Freq(freq, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_LFO_OSC_FREQ)
    outBA.append(slotNr)
    if freq > 31:
        freq = 31
    print ("SLOT", slotNr, "LFO OSC Freq:", freq)
    outBA.append(freq)
    posix.write(pipe, outBA)

def Slot_LFO_Reset(bReset,slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_LFO_RESET)
    outBA.append(slotNr)
    outBA.append(bReset)
    posix.write(pipe, outBA)

def Slot_ALFO_Shape(shape, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_ALFO_SHAPE)
    outBA.append(slotNr)
    if shape > 3:
        shape = 3
    print ("SLOT", slotNr, "ALFO Shape:", shape)
    outBA.append(shape)
    posix.write(pipe, outBA)

def Slot_ALFO_Level(level, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_ALFO_LEVEL)
    outBA.append(slotNr)
    if level > 7:
        level = 7
    print ("SLOT", slotNr, "ALFO Level:", level)
    outBA.append(level)
    posix.write(pipe, outBA)

def Slot_PLFO_Shape(shape, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_PLFO_SHAPE)
    outBA.append(slotNr)
    if shape > 3:
        shape = 3
    print ("SLOT", slotNr, "PLFO Shape:", shape)
    outBA.append(shape)
    posix.write(pipe, outBA)

def Slot_PLFO_Level(level, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_PLFO_LEVEL)
    outBA.append(slotNr)
    if level > 7:
        level = 7
    print ("SLOT", slotNr, "PLFO Level:", level)
    outBA.append(level)
    posix.write(pipe, outBA)

def Slot_Midi_Note_On(MidiNoteNr, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_MIDI_NOTE_ON)
    outBA.append(slotNr)
    if ( MidiNoteNr < 0) or (MidiNoteNr > 127) :
        return
    print ("SLOT", slotNr, "Midi Note ON:", MidiNoteNr)
    outBA.append(MidiNoteNr)
    posix.write(pipe, outBA)

def Slot_Midi_Note_Off(MidiNoteNr, slotNr):
    outBA = bytearray()
    outBA.append(CMD_SLOT_MIDI_NOTE_OFF)
    outBA.append(slotNr)
    if ( MidiNoteNr < 0) or (MidiNoteNr > 127) :
        return
    print ("SLOT", slotNr, "Midi Note OFF:", MidiNoteNr)
    outBA.append(MidiNoteNr)
    posix.write(pipe, outBA)
