# SimpleOS - A Basic Operating System

SimpleOS is a minimal operating system written from scratch in C and x86 assembly. It demonstrates the fundamental concepts of operating system design including bootloading, memory management, process management, file systems, and user interfaces.

## Features

### Core Components

1. **Bootloader** (`src/boot/bootloader.asm`)
   - 512-byte x86 bootloader
   - Loads kernel from disk sectors
   - Basic error handling

2. **Kernel** (`src/kernel/kernel.c`)
   - Memory management with bitmap allocation
   - Process management with round-robin scheduling
   - System call interface
   - Video memory management for text output

3. **Shell** (`src/shell/shell.c`)
   - Command-line interface
   - Built-in commands (help, clear, echo, ls, cd, pwd, exit)
   - Command parsing and execution

4. **File System** (`src/fs/filesystem.c`)
   - Simple hierarchical file system
   - File and directory operations
   - Memory-based storage (not persistent)

### System Architecture

- **Architecture**: x86 (32-bit)
- **Memory Model**: Protected mode with paging
- **Process Model**: Cooperative multitasking
- **File System**: In-memory hierarchical structure
- **User Interface**: Text-based command shell

## Building SimpleOS

### Prerequisites

Install the required development tools:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nasm gcc-multilib qemu-system-x86

# CentOS/RHEL/Fedora
sudo yum install nasm gcc-multilib qemu-system-x86

# macOS (using Homebrew)
brew install nasm gcc qemu
```

### Build Instructions

1. Navigate to the project directory:
   ```bash
   cd os_project
   ```

2. Build the operating system:
   ```bash
   make all
   ```

3. Run in QEMU emulator:
   ```bash
   make run
   ```

### Build Targets

- `make all` - Build the complete OS
- `make clean` - Remove build files
- `make run` - Run OS in QEMU
- `make debug` - Run OS in QEMU with debug support
- `make install-deps` - Install required packages
- `make help` - Show available targets

## Project Structure

```
os_project/
├── src/
│   ├── boot/
│   │   └── bootloader.asm      # x86 bootloader
│   ├── kernel/
│   │   └── kernel.c            # Main kernel code
│   ├── shell/
│   │   └── shell.c             # Command shell
│   └── fs/
│       └── filesystem.c        # File system implementation
├── include/
│   └── kernel.h                # Kernel header file
├── bin/                        # Build output directory
├── obj/                        # Object files directory
├── Makefile                    # Build configuration
├── linker.ld                   # Linker script
└── README.md                   # This file
```

## System Components

### Memory Management

The kernel implements a simple bitmap-based memory allocator:

- Pages are 4KB each
- Bitmap tracks allocated/free pages
- Supports up to 1024 pages (4MB total)
- Memory starts at 1MB (0x100000)

### Process Management

- Supports up to 10 concurrent processes
- Round-robin scheduling
- Process states: Ready, Running, Blocked, Terminated
- Each process gets 4KB stack space

### File System

- Hierarchical directory structure
- In-memory storage (not persistent)
- Supports up to 100 files and 50 directories
- File permissions (read, write, execute)
- Maximum file size: 4KB

### Shell Commands

- `help` - Show available commands
- `clear` - Clear the screen
- `echo [text]` - Print text
- `ls` - List files and directories
- `cd [directory]` - Change directory
- `pwd` - Print working directory
- `exit` - Exit the shell

## System Calls

The kernel provides these system calls:

- `SYS_WRITE` (1) - Write to output
- `SYS_READ` (2) - Read from input
- `SYS_EXIT` (3) - Terminate process
- `SYS_FORK` (4) - Create new process
- `SYS_EXEC` (5) - Execute program

## Development

### Adding New Features

1. **New System Calls**: Add to `kernel.c` and update system call handler
2. **New Shell Commands**: Add to `shell.c` and update command parser
3. **New File System Features**: Extend `filesystem.c`
4. **Hardware Support**: Add drivers in `src/drivers/`

### Debugging

Use the debug target to run with GDB support:

```bash
make debug
```

Then connect GDB to QEMU:

```bash
gdb -ex "target remote localhost:1234" -ex "symbol-file bin/kernel.bin"
```

## Limitations

This is a learning project with several limitations:

- No persistent storage (file system is in-memory)
- Limited memory (4MB total)
- No networking support
- No graphics beyond text mode
- No real hardware drivers
- No security features
- No user accounts or permissions

## Future Enhancements

Potential improvements for a more complete OS:

- Persistent file system with disk I/O
- Virtual memory with demand paging
- Preemptive multitasking
- Inter-process communication
- Network stack
- Graphics support
- Real hardware drivers
- Security and user management
- Package management system

## License

This project is provided as educational material. Feel free to use, modify, and learn from it.

## Contributing

This is a learning project, but suggestions and improvements are welcome. Please focus on educational value and code clarity.

## Resources

For learning more about operating system development:

- [OSDev Wiki](https://wiki.osdev.org/)
- [Bran's Kernel Development Tutorial](http://www.osdever.net/bkerndev/)
- [Operating Systems: Three Easy Pieces](http://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Modern Operating Systems](https://www.amazon.com/Modern-Operating-Systems-Andrew-Tanenbaum/dp/013359162X)