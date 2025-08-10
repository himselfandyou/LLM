# Windows 11-inspired OS Makefile
# This Makefile builds a complete Windows 11-style operating system

# Compiler and assembler
CC = gcc
AS = nasm
LD = ld

# Flags
CFLAGS = -m32 -fno-pie -fno-stack-protector -nostdlib -nostdinc -fno-builtin -fno-pic -mno-red-zone -Wall -Wextra
ASFLAGS = -f elf32
LDFLAGS = -m elf_i386 -T linker.ld

# Directories
SRCDIR = src
INCDIR = include
BINDIR = bin
OBJDIR = obj
ASSETSDIR = assets

# Source files
BOOTLOADER_SRC = $(SRCDIR)/boot/bootloader.asm
KERNEL_SRC = $(SRCDIR)/kernel/kernel.c
GUI_SRC = $(SRCDIR)/gui/gui_system.c
FILE_EXPLORER_SRC = $(SRCDIR)/apps/file_explorer.c
SETTINGS_SRC = $(SRCDIR)/apps/settings.c
KEYBOARD_SRC = $(SRCDIR)/drivers/keyboard.c
MOUSE_SRC = $(SRCDIR)/drivers/mouse.c

# Object files
BOOTLOADER_OBJ = $(BINDIR)/bootloader.bin
KERNEL_OBJ = $(OBJDIR)/kernel.o
GUI_OBJ = $(OBJDIR)/gui_system.o
FILE_EXPLORER_OBJ = $(OBJDIR)/file_explorer.o
SETTINGS_OBJ = $(OBJDIR)/settings.o
KEYBOARD_OBJ = $(OBJDIR)/keyboard.o
MOUSE_OBJ = $(OBJDIR)/mouse.o

# Final output
OS_IMAGE = $(BINDIR)/win11_os.img

# Default target
all: $(OS_IMAGE)

# Create directories
$(BINDIR):
	mkdir -p $(BINDIR)

$(OBJDIR):
	mkdir -p $(OBJDIR)

# Build bootloader
$(BOOTLOADER_OBJ): $(BOOTLOADER_SRC) | $(BINDIR)
	@echo "Building bootloader..."
	$(AS) -f bin -o $@ $<

# Build kernel object files
$(KERNEL_OBJ): $(KERNEL_SRC) | $(OBJDIR)
	@echo "Building kernel..."
	$(CC) $(CFLAGS) -c -o $@ $<

$(GUI_OBJ): $(GUI_SRC) | $(OBJDIR)
	@echo "Building GUI system..."
	$(CC) $(CFLAGS) -c -o $@ $<

$(FILE_EXPLORER_OBJ): $(FILE_EXPLORER_SRC) | $(OBJDIR)
	@echo "Building File Explorer..."
	$(CC) $(CFLAGS) -c -o $@ $<

$(SETTINGS_OBJ): $(SETTINGS_SRC) | $(OBJDIR)
	@echo "Building Settings app..."
	$(CC) $(CFLAGS) -c -o $@ $<

$(KEYBOARD_OBJ): $(KEYBOARD_SRC) | $(OBJDIR)
	@echo "Building keyboard driver..."
	$(CC) $(CFLAGS) -c -o $@ $<

$(MOUSE_OBJ): $(MOUSE_SRC) | $(OBJDIR)
	@echo "Building mouse driver..."
	$(CC) $(CFLAGS) -c -o $@ $<

# Link kernel
$(BINDIR)/kernel.bin: $(KERNEL_OBJ) $(GUI_OBJ) $(FILE_EXPLORER_OBJ) $(SETTINGS_OBJ) $(KEYBOARD_OBJ) $(MOUSE_OBJ) linker.ld | $(BINDIR)
	@echo "Linking kernel..."
	$(LD) $(LDFLAGS) -o $@ $(KERNEL_OBJ) $(GUI_OBJ) $(FILE_EXPLORER_OBJ) $(SETTINGS_OBJ) $(KEYBOARD_OBJ) $(MOUSE_OBJ)

# Create OS image
$(OS_IMAGE): $(BOOTLOADER_OBJ) $(BINDIR)/kernel.bin | $(BINDIR)
	@echo "Creating OS image..."
	dd if=/dev/zero of=$@ bs=512 count=2880 2>/dev/null
	dd if=$(BOOTLOADER_OBJ) of=$@ conv=notrunc 2>/dev/null
	dd if=$(BINDIR)/kernel.bin of=$@ conv=notrunc seek=1 2>/dev/null
	@echo "Windows 11-inspired OS built successfully!"

# Clean build files
clean:
	@echo "Cleaning build files..."
	rm -rf $(BINDIR) $(OBJDIR)
	@echo "Clean complete."

# Run in QEMU
run: $(OS_IMAGE)
	@echo "Starting Windows 11-inspired OS in QEMU..."
	qemu-system-i386 -fda $(OS_IMAGE) -m 64 -display gtk -vga std

# Run in QEMU with debug
debug: $(OS_IMAGE)
	@echo "Starting Windows 11-inspired OS in QEMU debug mode..."
	@echo "Connect GDB with: gdb -ex 'target remote localhost:1234' -ex 'symbol-file bin/kernel.bin'"
	qemu-system-i386 -fda $(OS_IMAGE) -m 64 -s -S -display gtk -vga std

# Run in QEMU with better graphics
run-vga: $(OS_IMAGE)
	@echo "Starting Windows 11-inspired OS with VGA graphics..."
	qemu-system-i386 -fda $(OS_IMAGE) -m 64 -display gtk -vga std -soundhw all

# Install dependencies (Ubuntu/Debian)
install-deps:
	@echo "Installing build dependencies..."
	sudo apt-get update
	sudo apt-get install -y nasm gcc-multilib qemu-system-x86 make
	@echo "Dependencies installed."

# Install dependencies (CentOS/RHEL/Fedora)
install-deps-rpm:
	@echo "Installing build dependencies..."
	sudo yum install -y nasm gcc-multilib qemu-system-x86 make
	@echo "Dependencies installed."

# Install dependencies (macOS)
install-deps-mac:
	@echo "Installing build dependencies..."
	brew install nasm gcc qemu make
	@echo "Dependencies installed."

# Build documentation
docs:
	@echo "Generating documentation..."
	@mkdir -p docs
	@echo "# Windows 11-inspired OS Documentation" > docs/README.md
	@echo "" >> docs/README.md
	@echo "## Architecture" >> docs/README.md
	@echo "- Bootloader: x86 assembly bootloader with Windows 11 branding" >> docs/README.md
	@echo "- Kernel: C-based kernel with GUI support" >> docs/README.md
	@echo "- GUI: Modern Windows 11-style interface" >> docs/README.md
	@echo "- Apps: File Explorer, Settings, and more" >> docs/README.md
	@echo "" >> docs/README.md
	@echo "## Building" >> docs/README.md
	@echo "Run 'make all' to build the complete OS" >> docs/README.md
	@echo "" >> docs/README.md
	@echo "## Running" >> docs/README.md
	@echo "Run 'make run' to start the OS in QEMU" >> docs/README.md
	@echo "Documentation generated in docs/"

# Check code style
style-check:
	@echo "Checking code style..."
	@if command -v clang-format >/dev/null 2>&1; then \
		find $(SRCDIR) -name "*.c" -exec clang-format --dry-run {} \; ; \
	else \
		echo "clang-format not found. Install it for style checking." ; \
	fi

# Format code
format:
	@echo "Formatting code..."
	@if command -v clang-format >/dev/null 2>&1; then \
		find $(SRCDIR) -name "*.c" -exec clang-format -i {} \; ; \
		echo "Code formatted." ; \
	else \
		echo "clang-format not found. Install it for code formatting." ; \
	fi

# Create release package
release: all docs
	@echo "Creating release package..."
	@mkdir -p release
	@cp $(OS_IMAGE) release/
	@cp -r docs release/
	@cp README.md release/
	@cp LICENSE release/ 2>/dev/null || echo "No LICENSE file found"
	@tar -czf win11_os_release.tar.gz release/
	@rm -rf release/
	@echo "Release package created: win11_os_release.tar.gz"

# Show build information
info:
	@echo "Windows 11-inspired OS Build Information"
	@echo "========================================"
	@echo "Compiler: $(CC)"
	@echo "Assembler: $(AS)"
	@echo "Linker: $(LD)"
	@echo "Source directory: $(SRCDIR)"
	@echo "Output directory: $(BINDIR)"
	@echo "Object directory: $(OBJDIR)"
	@echo ""
	@echo "Available targets:"
	@echo "  all          - Build the complete OS"
	@echo "  clean        - Remove build files"
	@echo "  run          - Run OS in QEMU"
	@echo "  debug        - Run OS in QEMU with debug"
	@echo "  run-vga      - Run OS with VGA graphics"
	@echo "  install-deps - Install required packages"
	@echo "  docs         - Generate documentation"
	@echo "  style-check  - Check code style"
	@echo "  format       - Format code"
	@echo "  release      - Create release package"
	@echo "  info         - Show this information"

# Help target
help: info

# Phony targets
.PHONY: all clean run debug run-vga install-deps install-deps-rpm install-deps-mac docs style-check format release info help