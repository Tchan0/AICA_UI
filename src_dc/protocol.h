/*******************************************************************************
*
*******************************************************************************/
#ifndef __PROTOCOL_H_DEFINED__
#define __PROTOCOL_H_DEFINED__

/*******************************************************************************
* commands used in protocol between Python=PC & C=Dreamcast
*******************************************************************************/
#define DAC_ENABLE       0x01
#define DAC_DISABLE      0x02 //TODO: REMOVE THIS, does not exist
#define DAC_MONO         0x03
#define DAC_STEREO       0x04
#define DAC_VOLUME       0x05

#define SLOT_ENABLE      0x06
#define SLOT_DISABLE     0x07
#define SLOT_ISNOISE     0x08
#define SLOT_ISSOUND     0x09
#define SLOT_VOLUME      0x0A
#define SLOT_PANNING     0x0B
#define SLOT_LOOP_ON     0x0C
#define SLOT_LOOP_OFF    0x0D
#define SLOT_LOOP_START  0x0E
#define SLOT_LOOP_END    0x0F
#define SLOT_ATTACK      0x10
#define SLOT_DECAY1      0x11
#define SLOT_DECAY2      0x12
#define SLOT_RELEASE     0x13
#define SLOT_FORMAT      0x14
#define SLOT_RAMPTR      0x15

#define SLOT_LFO_OSC_FREQ    0x20
#define SLOT_LFO_RESET       0x21
#define SLOT_ALFO_SHAPE      0x22
#define SLOT_ALFO_LEVEL      0x23
#define SLOT_PLFO_SHAPE      0x24
#define SLOT_PLFO_LEVEL      0x25

#define SLOT_MIDI_NOTE_ON    0x30
#define SLOT_MIDI_NOTE_OFF   0x31

#define LOAD_WAVEDATA    0x50

#define SLOT_DSPVOLUME   0x60 //TODO: temp ID

/*******************************************************************************
* Function declarations
*******************************************************************************/
int executeCommands (file_t fin);

#endif