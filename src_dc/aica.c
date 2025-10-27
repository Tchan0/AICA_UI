/*******************************************************************************
* 
*******************************************************************************/
#include <stdio.h>

#include <kos.h>

#include "aica.h"

/*******************************************************************************
* AICA common registers
*******************************************************************************/
AICA_REGISTER AicaRegs[] = {
    { CMNREGADDR(0), 0x000F,  0, "DAC_VOLUME"}, //AICA_MVOL
    { CMNREGADDR(0), 0x8000, 15, "DAC_MONO"}    //AICA_MONO
};

/*******************************************************************************
* AICA slot registers
*******************************************************************************/
AICA_REGISTER AicaSlotRegs[] = {
    {CHNREGADDR(0, 0x00) , 0x007F,   0, "SLOT_SRC_ADDR_H"},                 //AICA_SLOT_SRC_ADDR_H
    {CHNREGADDR(0, 0x00) , 0x0180,   7, "SLOT_FORMAT"},                     //AICA_SLOT_FORMAT
    {CHNREGADDR(0, 0x00) , 0x0200,   9, "SLOT_LOOPING"},                    //AICA_SLOT_LOOPING
    {CHNREGADDR(0, 0x00) , 0x0400,  10, "SLOT_NOISE"},                      //AICA_SLOT_NOISE
    {CHNREGADDR(0, 0x00) , 0x4000,  14, "SLOT_ON"},                         //AICA_SLOT_ON
    {CHNREGADDR(0, 0x00) , 0x8000,  15, "SLOT_ALL_ON"},                     //AICA_SLOT_ALL_ON

    {CHNREGADDR(0, 0x04) , 0xFFFF,   0, "SLOT_SRC_ADDR_L"},                 //AICA_SLOT_SRC_ADDR_L
    {CHNREGADDR(0, 0x08) , 0xFFFF,   0, "SLOT_LOOPSTART"},                  //AICA_SLOT_LOOPSTART
    {CHNREGADDR(0, 0x0C) , 0xFFFF,   0, "SLOT_LOOPEND"},                    //AICA_SLOT_LOOPEND

    {CHNREGADDR(0, 0x10) , 0x001F,   0, "SLOT_ATTACK"},                     //AICA_SLOT_ATTACK                   //AMPLITUDE ENVELOPE (GENERATOR)
    {CHNREGADDR(0, 0x10) , 0x07C0,   6, "SLOT_DECAY1"},                     //AICA_SLOT_DECAY1                   //AMPLITUDE ENVELOPE
    {CHNREGADDR(0, 0x10) , 0xF800,  11, "SLOT_DECAY2"},                     //AICA_SLOT_DECAY2                   //AMPLITUDE ENVELOPE

    {CHNREGADDR(0, 0x14) , 0x001F,   0, "SLOT_RELEASE"},                    //AICA_SLOT_RELEASE                  //AMPLITUDE ENVELOPE
    {CHNREGADDR(0, 0x14) , 0x03E0,   5, "SLOT_DECAY1_TO_2_LEVEL"},          //AICA_SLOT_DECAY1_TO_2_LEVEL        //AMPLITUDE ENVELOPE
    {CHNREGADDR(0, 0x14) , 0x3C00,  10, "SLOT_EG_KEY_RATE_SCALING"},        //AICA_SLOT_EG_KEY_RATE_SCALING      //AMPLITUDE ENVELOPE
    {CHNREGADDR(0, 0x14) , 0x4000,  14, "SLOT_LOOPSTART_LINK"},             //AICA_SLOT_LOOPSTART_LINK           //AMPLITUDE ENVELOPE when looping

    {CHNREGADDR(0, 0x18) , 0x03FF,   0, "SLOT_PITCH_FNUMBER"},              //AICA_SLOT_PITCH_FNUMBER            //PG = Phase Generator = which key is pressed (OCT=FNS=0 = original sample)
    {CHNREGADDR(0, 0x18) , 0x7800,  11, "SLOT_OCTAVE"},                     //AICA_SLOT_OCTAVE                   //PG

    {CHNREGADDR(0, 0x1C) , 0x0007,   0, "SLOT_LFO_TO_EG_MIX"},              //AICA_SLOT_LFO_TO_EG_MIX            //LFO -> EG amplitude (0=no effect, 7 = max attenuation)
    {CHNREGADDR(0, 0x1C) , 0x0018,   3, "SLOT_ALFO_WAVESHAPE"},             //AICA_SLOT_ALFO_WAVESHAPE           //LFO -> EG amplitude (4 wavetypes)
    {CHNREGADDR(0, 0x1C) , 0x00E0,   5, "SLOT_LFO_TO_PITCH_MIX"},           //AICA_SLOT_LFO_TO_PITCH_MIX         //LFO ->              (0=no effect, 7=max displacement)
    {CHNREGADDR(0, 0x1C) , 0x0300,   8, "SLOT_PLFO_WAVESHAPE"},             //AICA_SLOT_PLFO_WAVESHAPE           //LFO ->              (4 wavetypes)
    {CHNREGADDR(0, 0x1C) , 0x7C00,  10, "AICA_SLOT_LFO_OSC_FREQ"},          //AICA_SLOT_LFO_OSC_FREQ             //LFO: 0.17 Hz to 172.3 Hz
    {CHNREGADDR(0, 0x1C) , 0x8000,  15, "SLOT_LFO_RESET"},                  //AICA_SLOT_LFO_RESET                //LFO

    {CHNREGADDR(0, 0x20) , 0x000F,   0, "SLOT_DSP_MIXS_REG"},               //AICA_SLOT_DSP_MIXS_REG
    {CHNREGADDR(0, 0x20) , 0x00F0,   4, "SLOT_DSP_LEVEL"},                  //AICA_SLOT_DSP_LEVEL

    {CHNREGADDR(0, 0x24) , 0x001F,   0, "SLOT_DAC_PANNING"},                //AICA_SLOT_DAC_PANNING
    {CHNREGADDR(0, 0x24) , 0x0F00,   8, "SLOT_DAC_LEVEL"},                  //AICA_SLOT_DAC_LEVEL

    {CHNREGADDR(0, 0x28) , 0x001F,   0, "SLOT_RESONANCE_Q_LEVEL"},          //AICA_SLOT_RESONANCE_Q_LEVEL
    {CHNREGADDR(0, 0x28) , 0xFF00,   8, "SLOT_TOTAL_LEVEL"},                //AICA_SLOT_TOTAL_LEVEL

//LPF with a cutoff frequency that can be varied over time for all channels
    {CHNREGADDR(0, 0x2C) , 0x1FFF,   0, "SLOT_FILTER_CUTOFF_ATTACK_START"}, //AICA_SLOT_FILTER_CUTOFF_ATTACK_START (LPF, init to 0x1FF8 to pass everything (no cutoff))
    {CHNREGADDR(0, 0x30) , 0x1FFF,   0, "SLOT_FILTER_CUTOFF_ATTACK_END"},   //AICA_SLOT_FILTER_CUTOFF_ATTACK_END   (LPF, init to 0x1FF8 to pass everything (no cutoff))
    {CHNREGADDR(0, 0x34) , 0x1FFF,   0, "SLOT_FILTER_CUTOFF_DECAY_END"},    //AICA_SLOT_FILTER_CUTOFF_DECAY_END    (LPF, init to 0x1FF8 to pass everything (no cutoff))
    {CHNREGADDR(0, 0x38) , 0x1FFF,   0, "SLOT_FILTER_CUTOFF_KOFF"},         //AICA_SLOT_FILTER_CUTOFF_KOFF         (LPF, init to 0x1FF8 to pass everything (no cutoff))
    {CHNREGADDR(0, 0x3C) , 0x1FFF,   0, "SLOT_FILTER_CUTOFF_RELEASE"},      //AICA_SLOT_FILTER_CUTOFF_RELEASE      (LPF, init to 0x1FF8 to pass everything (no cutoff))

    {CHNREGADDR(0, 0x40) , 0x001F,   0, "SLOT_FILTER_DECAY1"},              //AICA_SLOT_FILTER_DECAY1
    {CHNREGADDR(0, 0x40) , 0x1F00,   8, "SLOT_FILTER_ATTACK"},              //AICA_SLOT_FILTER_ATTACK

    {CHNREGADDR(0, 0x44) , 0x001F,   0, "SLOT_FILTER_RELEASE"},             //AICA_SLOT_FILTER_RELEASE
    {CHNREGADDR(0, 0x44) , 0x1F00,   8, "SLOT_FILTER_DECAY2"},              //AICA_SLOT_FILTER_DECAY2
};

/*******************************************************************************
* change a AICA common register
*******************************************************************************/
void aicaChangeValue (int reg, uint16_t val16){
 uint32_t val = 0;
 uint32_t addr = AicaRegs[reg].address;

 printf("%s: %d\n", AicaRegs[reg].desc, val16);

 g2_fifo_wait();
 if (AicaRegs[reg].bitSelection != 0xFFFF) //don't bother reading the current state, if we're gonna overwrite everything anyways
    val = g2_read_32(addr) & ~AicaRegs[reg].bitSelection;
 
 val |= (val16 << AicaRegs[reg].shiftBits);

 g2_write_32 (addr, val);
}

/*******************************************************************************
* change a AICA SLOT register
*******************************************************************************/
void aicaChangeSlotValue (int slotNr, int reg, uint16_t val16){
 uint32_t val = 0;
 uint32_t addr = (AicaSlotRegs[reg].address) + (slotNr * 0x80);

 printf("%d:%s: %d\n", slotNr, AicaSlotRegs[reg].desc, val16);

 g2_fifo_wait();
 if (AicaSlotRegs[reg].bitSelection != 0xFFFF) //don't bother reading the current state, if we're gonna overwrite everything anyways
    val = g2_read_32(addr) & ~AicaSlotRegs[reg].bitSelection;
 
 //TODO special case: SLOT_ALL_ON: KYONEX: always write 1, 0 is not accepted (it auto-resets).
 //   effect: if 1 is written to Kyonex: if at least 1 key is on, it will play it/them.
 //                                    : if no keys are on, it switch to status "off"
 if (reg == AICA_SLOT_ALL_ON) { val16 = 1; val &= 0x7FFF;} //TODO 0x7FFF temp hack
 else if (AicaSlotRegs[reg].address == 0xa0700000) val &= 0x7FFF; //force-avoid that KYONEX is 1 when other regs than KYONEX are updated
  
 val |= (val16 << AicaSlotRegs[reg].shiftBits);

 g2_write_32 (addr, val);
}

/*******************************************************************************
*
*******************************************************************************/
void aicaSetSlotSrcAddress (int slotNr, uint32_t addr){
 uint16_t val16;

 val16 = (addr >> 16) & 0xFFFF;
 aicaChangeSlotValue (AICA_SLOT_SRC_ADDR_H, slotNr, val16);
 val16 = (addr & 0xFFFF);
 aicaChangeSlotValue (AICA_SLOT_SRC_ADDR_L, slotNr, val16);  
}

/*******************************************************************************
*
*******************************************************************************/
void aicaSetSlotNote (int slotNr, int8_t oct, uint16_t fns){
 uint32_t val;
 uint32_t addr = (AicaSlotRegs[AICA_SLOT_OCTAVE].address) + (slotNr * 0x80);

 printf("%d:%s: OCT:0x%02X - FNS:0x%04X\n", slotNr, "SLOT_NOTE", oct, fns);

 g2_fifo_wait();
 val = (oct << AicaSlotRegs[AICA_SLOT_OCTAVE].shiftBits) | (fns << AicaSlotRegs[AICA_SLOT_PITCH_FNUMBER].shiftBits);
 g2_write_32 (addr, val);
}
