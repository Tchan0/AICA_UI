# Put the filename of the output binary here
TARGET = AICA_UI.elf

# List all of your C files here, but change the extension to ".o"
# Include "romdisk.o" to the OBJS, and uncomment KOS_ROMDISK_DIR if you want a rom disk.
OBJS = AICA_UI.o aica.o protocol.o
#KOS_ROMDISK_DIR = romdisk

all: rm-elf $(TARGET)

include $(KOS_BASE)/Makefile.rules

clean: rm-elf
	-rm -f $(OBJS)

rm-elf:
	-rm -f ../bin/$(TARGET)

$(TARGET): $(OBJS)
	kos-cc -o ../bin/$(TARGET) $(OBJS)

run: $(TARGET)
	$(KOS_LOADER) ../bin/$(TARGET)

dist: $(TARGET)
	-rm -f $(OBJS) romdisk.img
	$(KOS_STRIP) ../bin/$(TARGET)

send:
	dc-tool-ip -t 192.168.1.210 -x ./AICA_UI.elf
# /opt/toolchains/dc/bin/dc-tool-ser -t /dev/ttyUSB0 -b 1562500 -x ./AICA_UI.elf   520833 390625 312500 260416 223214
# /opt/toolchains/dc/bin/dc-tool-ser -t /dev/ttyUSB0 -b 781250 -x ./AICA_UI.elf
# /opt/toolchains/dc/bin/dc-tool-ser -t /dev/ttyUSB0 -b 115200 -x ./AICA_UI.elf
# /opt/toolchains/dc/bin/dc-tool-ser -t /dev/ttyACM0 -b 115200 -x ./nehe06.elf
