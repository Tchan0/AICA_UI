class AICAUtils():

    def setPortColorDisabled(port):
        port.color        = (255, 0, 0)
        port.border_color = (255, 0, 0)

    def setPortColorEnabled(port):
        port.color        = (0, 255, 0)
        port.border_color = (0, 255, 0)


# constants for the YAMAHA AICA
# =============================
# Volume Levels (IMXL, DISDL, EFSDL, MVOL)
#0	'-MAX	db Attenuation
#1	-42	db Attenuation
#2	-39	db Attenuation
#3	36	db Attenuation
#4	33	db Attenuation
#5	30	db Attenuation
#6	27	db Attenuation
#7	24	db Attenuation
#8	21	db Attenuation
#9	18	db Attenuation
#10	15	db Attenuation
#11	12	db Attenuation
#12	9	db Attenuation
#13	6	db Attenuation
#14	3	db Attenuation
#15	0	db Attenuation

#DIPAN, EFPAN
#Left_MAX       center        RIGHT_MAX
#0x1F            0x00          0x0F        AICA
# -15               0           15         Qt