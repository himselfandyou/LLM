#!/bin/bash

# SimpleOS Build Script
# This script builds the complete operating system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking build dependencies..."
    
    local missing_deps=()
    
    if ! command_exists nasm; then
        missing_deps+=("nasm")
    fi
    
    if ! command_exists gcc; then
        missing_deps+=("gcc")
    fi
    
    if ! command_exists ld; then
        missing_deps+=("binutils")
    fi
    
    if ! command_exists qemu-system-i386; then
        missing_deps+=("qemu-system-x86")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_status "Installing dependencies..."
        
        if command_exists apt-get; then
            # Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y nasm gcc-multilib qemu-system-x86
        elif command_exists yum; then
            # CentOS/RHEL/Fedora
            sudo yum install -y nasm gcc-multilib qemu-system-x86
        elif command_exists brew; then
            # macOS
            brew install nasm gcc qemu
        else
            print_error "Could not determine package manager. Please install dependencies manually:"
            print_error "  - nasm (Netwide Assembler)"
            print_error "  - gcc-multilib (GNU Compiler Collection)"
            print_error "  - qemu-system-x86 (QEMU emulator)"
            exit 1
        fi
    else
        print_success "All dependencies are installed"
    fi
}

# Function to clean build
clean_build() {
    print_status "Cleaning previous build..."
    make clean
    print_success "Build cleaned"
}

# Function to build OS
build_os() {
    print_status "Building SimpleOS..."
    
    # Create necessary directories
    mkdir -p bin obj
    
    # Build bootloader
    print_status "Building bootloader..."
    nasm -f bin -o bin/bootloader.bin src/boot/bootloader.asm
    
    # Build kernel components
    print_status "Building kernel components..."
    gcc -m32 -fno-pie -fno-stack-protector -nostdlib -nostdinc -fno-builtin -fno-pic -mno-red-zone -c -o obj/kernel.o src/kernel/kernel.c
    gcc -m32 -fno-pie -fno-stack-protector -nostdlib -nostdinc -fno-builtin -fno-pic -mno-red-zone -c -o obj/shell.o src/shell/shell.c
    gcc -m32 -fno-pie -fno-stack-protector -nostdlib -nostdinc -fno-builtin -fno-pic -mno-red-zone -c -o obj/filesystem.o src/fs/filesystem.c
    gcc -m32 -fno-pie -fno-stack-protector -nostdlib -nostdinc -fno-builtin -fno-pic -mno-red-zone -c -o obj/keyboard.o src/drivers/keyboard.c
    
    # Link kernel
    print_status "Linking kernel..."
    ld -m elf_i386 -T linker.ld -o bin/kernel.bin obj/kernel.o obj/shell.o obj/filesystem.o obj/keyboard.o
    
    # Create OS image
    print_status "Creating OS image..."
    dd if=/dev/zero of=bin/simpleos.img bs=512 count=2880 2>/dev/null
    dd if=bin/bootloader.bin of=bin/simpleos.img conv=notrunc 2>/dev/null
    dd if=bin/kernel.bin of=bin/simpleos.img conv=notrunc seek=1 2>/dev/null
    
    print_success "SimpleOS built successfully!"
    print_status "OS image created: bin/simpleos.img"
}

# Function to run OS
run_os() {
    if [ ! -f "bin/simpleos.img" ]; then
        print_error "OS image not found. Please build first with: $0 build"
        exit 1
    fi
    
    print_status "Starting SimpleOS in QEMU..."
    qemu-system-i386 -fda bin/simpleos.img -m 16 -display gtk
}

# Function to run OS in debug mode
debug_os() {
    if [ ! -f "bin/simpleos.img" ]; then
        print_error "OS image not found. Please build first with: $0 build"
        exit 1
    fi
    
    print_status "Starting SimpleOS in QEMU debug mode..."
    print_status "Connect GDB with: gdb -ex 'target remote localhost:1234' -ex 'symbol-file bin/kernel.bin'"
    qemu-system-i386 -fda bin/simpleos.img -m 16 -s -S -display gtk
}

# Function to show help
show_help() {
    echo "SimpleOS Build Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build the complete operating system"
    echo "  clean     Clean build files"
    echo "  run       Run the OS in QEMU"
    echo "  debug     Run the OS in QEMU with debug support"
    echo "  deps      Check and install dependencies"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build  # Build the OS"
    echo "  $0 run    # Run the OS"
    echo "  $0 debug  # Run with debug support"
}

# Main script logic
case "${1:-build}" in
    "build")
        check_dependencies
        clean_build
        build_os
        ;;
    "clean")
        clean_build
        ;;
    "run")
        run_os
        ;;
    "debug")
        debug_os
        ;;
    "deps")
        check_dependencies
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac