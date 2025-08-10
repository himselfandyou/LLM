# SimpleOS Makefile
# This Makefile builds a basic operating system

# Compiler and assembler
CC = gcc
AS = nasm
LD = ld

# Flags
CFLAGS = -m32 -fno-pie -fno-stack-protector -nostdlib -nostdinc -fno-builtin -fno-pic -mno-red-zone
ASFLAGS = -f elf32
LDFLAGS = -m elf_i386 -T linker.ld

# Directories
SRCDIR = src
INCDIR = include
BINDIR = bin
OBJDIR = obj

# Source files
BOOTLOADER_SRC = $(SRCDIR)/boot/bootloader.asm
KERNEL_SRC = $(SRCDIR)/kernel/kernel.c
SHELL_SRC = $(SRCDIR)/shell/shell.c
FS_SRC = $(SRCDIR)/fs/filesystem.c
KEYBOARD_SRC = $(SRCDIR)/drivers/keyboard.c

# Object files
BOOTLOADER_OBJ = $(BINDIR)/bootloader.bin
KERNEL_OBJ = $(OBJDIR)/kernel.o
SHELL_OBJ = $(OBJDIR)/shell.o
FS_OBJ = $(OBJDIR)/filesystem.o
KEYBOARD_OBJ = $(OBJDIR)/keyboard.o

# Final output
OS_IMAGE = $(BINDIR)/simpleos.img

# Default target
all: $(OS_IMAGE)

# Create directories
$(BINDIR):
	mkdir -p $(BINDIR)

$(OBJDIR):
	mkdir -p $(OBJDIR)

# Build bootloader
$(BOOTLOADER_OBJ): $(BOOTLOADER_SRC) | $(BINDIR)
	$(AS) -f bin -o $@ $<

# Build kernel object files
$(KERNEL_OBJ): $(KERNEL_SRC) | $(OBJDIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(SHELL_OBJ): $(SHELL_SRC) | $(OBJDIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(FS_OBJ): $(FS_SRC) | $(OBJDIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(KEYBOARD_OBJ): $(KEYBOARD_SRC) | $(OBJDIR)
	$(CC) $(CFLAGS) -c -o $@ $<

# Link kernel
$(BINDIR)/kernel.bin: $(KERNEL_OBJ) $(SHELL_OBJ) $(FS_OBJ) $(KEYBOARD_OBJ) linker.ld | $(BINDIR)
	$(LD) $(LDFLAGS) -o $@ $(KERNEL_OBJ) $(SHELL_OBJ) $(FS_OBJ) $(KEYBOARD_OBJ)

# Create OS image
$(OS_IMAGE): $(BOOTLOADER_OBJ) $(BINDIR)/kernel.bin | $(BINDIR)
	dd if=/dev/zero of=$@ bs=512 count=2880
	dd if=$(BOOTLOADER_OBJ) of=$@ conv=notrunc
	dd if=$(BINDIR)/kernel.bin of=$@ conv=notrunc seek=1

# Clean build files
clean:
	rm -rf $(BINDIR) $(OBJDIR)

# Run in QEMU
run: $(OS_IMAGE)
	qemu-system-i386 -fda $(OS_IMAGE) -m 16

# Run in QEMU with debug
debug: $(OS_IMAGE)
	qemu-system-i386 -fda $(OS_IMAGE) -m 16 -s -S

# Install dependencies (Ubuntu/Debian)
install-deps:
	sudo apt-get update
	sudo apt-get install -y nasm gcc-multilib qemu-system-x86

# Help
help:
	@echo "Available targets:"
	@echo "  all        - Build the complete OS"
	@echo "  clean      - Remove build files"
	@echo "  run        - Run OS in QEMU"
	@echo "  debug      - Run OS in QEMU with debug"
	@echo "  install-deps - Install required packages"

.PHONY: all clean run debug install-deps help