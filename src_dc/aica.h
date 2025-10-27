/*******************************************************************************
*
*******************************************************************************/
#ifndef __AICA_H_DEFINED__
#define __AICA_H_DEFINED__

#include <stdint.h>

/*******************************************************************************
* Some convenience macros from KallistiOs
*******************************************************************************/
#define SNDREGADDR(x) (0xa0700000 + (x))
#define CHNREGADDR(chn, x) SNDREGADDR(0x80*(chn) + (x))

#define CMNREGADDR(x) (0xa0702800 + (x))
#define AICA_COMMON 0x2800

#define AICA_RAM_START 0x00800000
#define AICA_RAM_MAX   0x009FFFFF // 2 MB RAM AICA (DREAMCAST, ATOMISWAVE)
//#define AICA_RAM_MAX   0x00FFFFFF // 8 MB RAM AICA (NAOMI 1/2, SYSTEM SP, HIKARU)

/*******************************************************************************
*
*******************************************************************************/
typedef struct {
 uint32_t address;
 uint16_t bitSelection;
 uint16_t shiftBits; 
 char*    desc;
} AICA_REGISTER;

/*******************************************************************************
* AICA common registers
*******************************************************************************/
#define AICA_MVOL 0      //DONE
#define AICA_MONO 1      //DONE

/*******************************************************************************
* AICA slot registers
*******************************************************************************/
#define AICA_SLOT_SRC_ADDR_H                  0 //SA[22:16]           zz
#define AICA_SLOT_FORMAT                      1 //PCMS                DONE      0=16bit PCM, 1=8bit PCM, 2=4bit ADPCM, 3=4bit ADPCM longstream
#define AICA_SLOT_LOOPING                     2 //LPCTL               DONE
#define AICA_SLOT_NOISE                       3 //SSCTL               DONE
#define AICA_SLOT_ON                          4 //KYONB               DONE
#define AICA_SLOT_ALL_ON                      5 //KYONEX              DONE
#define AICA_SLOT_SRC_ADDR_L                  6 //SA[15:0]            zz
#define AICA_SLOT_LOOPSTART                   7 //LSA                 DONE
#define AICA_SLOT_LOOPEND                     8 //LEA                 DONE
#define AICA_SLOT_ATTACK                      9 //AR                  DONE
#define AICA_SLOT_DECAY1                     10 //D1R                 zz
#define AICA_SLOT_DECAY2                     11 //D2R                 zz
#define AICA_SLOT_RELEASE                    12 //RR                  zz
#define AICA_SLOT_DECAY1_TO_2_LEVEL          13 //DL                  zz
#define AICA_SLOT_EG_KEY_RATE_SCALING        14 //KRS
#define AICA_SLOT_LOOPSTART_LINK             15 //LPSLNK
#define AICA_SLOT_PITCH_FNUMBER              16 //FNS                 zz
#define AICA_SLOT_OCTAVE                     17 //OCT                 zz
#define AICA_SLOT_LFO_TO_EG_MIX              18 //ALFOS
#define AICA_SLOT_ALFO_WAVESHAPE             19 //ALFOWS
#define AICA_SLOT_LFO_TO_PITCH_MIX           20 //PLFOS
#define AICA_SLOT_PLFO_WAVESHAPE             21 //PLFOWS
#define AICA_SLOT_LFO_OSC_FREQ               22 //LFOF
#define AICA_SLOT_LFO_RESET                  23 //LFORE
#define AICA_SLOT_DSP_MIXS_REG               24 //ISEL
#define AICA_SLOT_DSP_LEVEL                  25 //IMXL              DONE
#define AICA_SLOT_DAC_PANNING                26 //DIPAN             DONE
#define AICA_SLOT_DAC_LEVEL                  27 //DISDL             DONE
#define AICA_SLOT_RESONANCE_Q_LEVEL          28 //Q
#define AICA_SLOT_TOTAL_LEVEL                29 //TL
#define AICA_SLOT_FILTER_CUTOFF_ATTACK_START 30 //FLV0
#define AICA_SLOT_FILTER_CUTOFF_ATTACK_END   31 //FLV1
#define AICA_SLOT_FILTER_CUTOFF_DECAY_END    32 //FLV2
#define AICA_SLOT_FILTER_CUTOFF_KOFF         33 //FLV3
#define AICA_SLOT_FILTER_CUTOFF_RELEASE      34 //FLV4
#define AICA_SLOT_FILTER_DECAY1              35 //FD1R
#define AICA_SLOT_FILTER_ATTACK              36 //FAR
#define AICA_SLOT_FILTER_RELEASE             37 //FRR
#define AICA_SLOT_FILTER_DECAY2              38 //FD2R

/*******************************************************************************
* Function declarations
*******************************************************************************/
void aicaChangeValue (int reg, uint16_t val16);

void aicaChangeSlotValue (int slotNr, int reg, uint16_t val16);
void aicaSetSlotSrcAddress (int slotNr, uint32_t addr);
void aicaSetSlotNote (int slotNr, int8_t oct, uint16_t fns);

#endif