/*******************************************************************************
*
*******************************************************************************/
#include <stdio.h>

#include <kos.h>
//#include <stdlib.h>

#include "aica.h"
#include "protocol.h"

uint16_t FNSValues[] = {
 0x00,  0x3D,  0x7D,  0xC2,
 0x10A, 0x157, 0x1A8, 0x1FE,
 0x25A, 0x2BA, 0x321, 0x38D
};

/*******************************************************************************
* There are 128 possible notes on a MIDI device, numbered 0 to 127 (where Middle C is note number 60). 
*******************************************************************************/
uint16_t midi2FrequencyNumberSwitch (int midiNoteNr){
 uint16_t ret;

 ret = FNSValues[midiNoteNr % 12];

 return ret; 
}

/*******************************************************************************
* There are 128 possible notes on a MIDI device, numbered 0 to 127 (where Middle C is note number 60). 
*******************************************************************************/
int8_t midi2Octave (int midiNoteNr){
 int8_t ret;

 ret = (midiNoteNr / 12) - 5;

 return ret; 
}

/*******************************************************************************
*
*******************************************************************************/
int executeCommands (file_t fin){
 uint8_t cmd, vol, slotNr, pan, attack, byte2, freq, bReset, shape, level;
 uint16_t val16;

 fs_read(fin, &cmd, 1);
 switch (cmd){
    case DAC_ENABLE:
    //case DAC_DISABLE:
        aicaChangeSlotValue(0, AICA_SLOT_ALL_ON, 1);//cmd == DAC_ENABLE ? 1 : 0);
        break;

    case DAC_MONO:
    case DAC_STEREO:
        aicaChangeValue (AICA_MONO, cmd == DAC_MONO ? 1 : 0);
        break;

    case DAC_VOLUME:
        fs_read(fin, &vol, 1);
        aicaChangeValue (AICA_MVOL, vol > 15 ? 15 : vol);
        break;

    case SLOT_ENABLE:
    case SLOT_DISABLE:
        fs_read(fin, &slotNr, 1);
        if (slotNr > 63) break;
        aicaChangeSlotValue(slotNr, AICA_SLOT_ON,                         cmd == SLOT_ENABLE ? 1 : 0);
        aicaChangeSlotValue(slotNr, AICA_SLOT_FILTER_CUTOFF_ATTACK_START, 0x1FF8);//TODO TEMP HERE
        aicaChangeSlotValue(slotNr, AICA_SLOT_FILTER_CUTOFF_ATTACK_END,   0x1FF8);//TODO TEMP HERE
        aicaChangeSlotValue(slotNr, AICA_SLOT_FILTER_CUTOFF_DECAY_END,    0x1FF8);//TODO TEMP HERE
        aicaChangeSlotValue(slotNr, AICA_SLOT_FILTER_CUTOFF_KOFF,         0x1FF8);//TODO TEMP HERE
        aicaChangeSlotValue(slotNr, AICA_SLOT_FILTER_CUTOFF_RELEASE,      0x1FF8);//TODO TEMP HERE
        break;

    case SLOT_ISNOISE:
    case SLOT_ISSOUND:
        fs_read(fin, &slotNr, 1);
        if (slotNr > 63) break;
        aicaChangeSlotValue(slotNr, AICA_SLOT_NOISE, cmd == SLOT_ISNOISE ? 1 : 0);
        break;

    case SLOT_VOLUME:
        fs_read(fin, &slotNr, 1);
        if (slotNr > 63) break;
        fs_read(fin, &vol, 1);
        aicaChangeSlotValue(slotNr, AICA_SLOT_DAC_LEVEL, vol > 15 ? 15 : vol);
        break;

    case SLOT_PANNING:
        fs_read(fin, &slotNr, 1);
        if (slotNr > 63) break;
        fs_read(fin, &pan, 1);
        aicaChangeSlotValue(slotNr, AICA_SLOT_DAC_PANNING, pan > 31 ? 31 : pan);
        break;

    case SLOT_LOOP_ON:
    case SLOT_LOOP_OFF:
        fs_read(fin, &slotNr, 1);
        if (slotNr > 63) break;
        aicaChangeSlotValue(slotNr, AICA_SLOT_LOOPING, cmd == SLOT_LOOP_ON ? 1 : 0);
        break;

    case SLOT_LOOP_START:
    case SLOT_LOOP_END:
        fs_read(fin, &slotNr, 1);
        if (slotNr > 63) break;
        fs_read(fin, &val16, 2);
        aicaChangeSlotValue(slotNr, cmd == SLOT_LOOP_START ? AICA_SLOT_LOOPSTART : AICA_SLOT_LOOPEND, val16 > 65534 ? 65534 : val16);
        break;

    case SLOT_DSPVOLUME:
        fs_read(fin, &slotNr, 1);
        if (slotNr > 63) break;
        fs_read(fin, &vol, 1);
        aicaChangeSlotValue(slotNr, AICA_SLOT_DSP_LEVEL, vol > 15 ? 15 : vol);
        break;

    case SLOT_ATTACK:
        fs_read(fin, &slotNr, 1);
        if (slotNr > 63) break;
        fs_read(fin, &attack, 1);
        aicaChangeSlotValue(slotNr, AICA_SLOT_ATTACK, attack > 0x1F ? 0x1F : attack);
        break;

/*TODO
#define SLOT_DECAY1      0x11
#define SLOT_DECAY2      0x12
#define SLOT_RELEASE     0x13
*/
    case SLOT_FORMAT:
        fs_read(fin, &slotNr, 1);
        if (slotNr > 63) break;
        fs_read(fin, &byte2, 1);//format
        aicaChangeSlotValue(slotNr, AICA_SLOT_FORMAT, byte2 > 0x3 ? 0x3 : byte2);
        break;

    case SLOT_RAMPTR: {
        uint32_t addr;
        fs_read(fin, &slotNr, 1);
        if (slotNr > 63) break;
        fs_read(fin, &addr, 4);
        if ((addr < AICA_RAM_START) || (addr >= AICA_RAM_MAX)) //ptr to AICA RAM address, viewed from the SH-4(G2)
            break;
        aicaSetSlotSrcAddress (slotNr, addr - AICA_RAM_START); //slot address is addr viewed from ARM, so minus AICA_RAM_START
        }
        break;

    case LOAD_WAVEDATA: {
        uint32_t addr, orig_siz;
        uint8_t* pData;

        fs_read(fin, &addr, 4); //bytes 2-3-4-5: ptr to AICA RAM address
        if ((addr < AICA_RAM_START) || (addr >= AICA_RAM_MAX)){ //ptr to AICA RAM address, viewed from the SH-4(G2)
            printf("LOAD WAVE: ERROR: bad addr: 0x%08lX\n", addr);
            break;
        }
        fs_read(fin, &orig_siz, 4);  //bytes 6-7-8-9: size of wave data following
        if (addr + orig_siz >= AICA_RAM_MAX){
            printf("LOAD WAVE: ERROR: bad size: 0x%08lX\n", orig_siz);
            break;
        }

        printf("LOAD WAVE @ 0x%08lX (%lu)\n", addr, orig_siz);
        pData = malloc(orig_siz);
        if (pData){
            uint8_t* ptr = pData;
            uint32_t siz = orig_siz;
            uint32_t sizeToTransferToSPU = 0;
            ssize_t  sizeRead = 0;
            while (sizeRead != -1){
                sizeRead = fs_read(fin, ptr, siz); //xxx bytes: wave data
                if (sizeRead){
                    ptr += sizeRead;
                    siz -= sizeRead;
                    sizeToTransferToSPU += sizeRead;
                    if (!siz) break;
                }
            }
            if (sizeToTransferToSPU){
                spu_memload_sq((uintptr_t)addr, (void*)pData, (size_t)sizeToTransferToSPU); //send to SOUND RAM via store queue
                //spu_memload   ((uintptr_t)addr, (void*)pData, (size_t)sizeToTransferToSPU); //send to SOUND RAM via store queue
            }
            free (pData);
            printf("LOAD WAVE @ 0x%08lX: LOADED %ld bytes !\n", addr, sizeToTransferToSPU);
            if (orig_siz != sizeToTransferToSPU) printf("?? DIFF bytes to upload (%ld) vs uploaded (%ld) ??\n", orig_siz, sizeToTransferToSPU);
        } else {
            printf("LOAD WAVE @ 0x%08lX: FAILED ??\n", addr);
        }
        }
        break;

        case SLOT_LFO_OSC_FREQ:
            fs_read(fin, &slotNr, 1);
            if (slotNr > 63) break;
            fs_read(fin, &freq, 1);
            aicaChangeSlotValue(slotNr, AICA_SLOT_LFO_OSC_FREQ, freq > 31 ? 31 : freq);
            break;

        case SLOT_LFO_RESET:
            fs_read(fin, &slotNr, 1);
            if (slotNr > 63) break;
            fs_read(fin, &bReset, 1);
            aicaChangeSlotValue(slotNr, AICA_SLOT_LFO_RESET, bReset ? 1 : 0);
            break;

        case SLOT_ALFO_SHAPE:
            fs_read(fin, &slotNr, 1);
            if (slotNr > 63) break;
            fs_read(fin, &shape, 1);
            aicaChangeSlotValue(slotNr, AICA_SLOT_ALFO_WAVESHAPE, shape > 3 ? 3 : shape);
            break;

        case SLOT_ALFO_LEVEL:
            fs_read(fin, &slotNr, 1);
            if (slotNr > 63) break;
            fs_read(fin, &level, 1);
            aicaChangeSlotValue(slotNr, AICA_SLOT_LFO_TO_EG_MIX, level > 7 ? 7 : level);
            break;

        case SLOT_PLFO_SHAPE:
            fs_read(fin, &slotNr, 1);
            if (slotNr > 63) break;
            fs_read(fin, &shape, 1);
            aicaChangeSlotValue(slotNr, AICA_SLOT_PLFO_WAVESHAPE, shape > 3 ? 3 : shape);
            break;

        case SLOT_PLFO_LEVEL:
            fs_read(fin, &slotNr, 1);
            if (slotNr > 63) break;
            fs_read(fin, &level, 1);
            aicaChangeSlotValue(slotNr, AICA_SLOT_LFO_TO_PITCH_MIX, level > 7 ? 7 : level);
            break;

        case SLOT_MIDI_NOTE_ON: { //TODO: MIDI CHANNEL + velocity
            int8_t midiNoteNr, oct;
            uint16_t fns;
            fs_read(fin, &slotNr, 1);
            if (slotNr > 63) break;
            fs_read(fin, &midiNoteNr, 1);
            if (midiNoteNr < 0) break;
            oct = midi2Octave(midiNoteNr);
            fns = midi2FrequencyNumberSwitch (midiNoteNr);
            aicaSetSlotNote (slotNr, oct, fns);
            //TODO ? -> set key_on & dac on ?
            }
            break;

        case SLOT_MIDI_NOTE_OFF: //TODO: MIDI CHANNEL + velocity
            //TODO: MUST: A Note On message that has a velocity of 0 is considered to actually be a Note Off message
            break;

    default:
        break;
 }

 return (1);
}

