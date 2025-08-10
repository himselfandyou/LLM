# SimpleOS Project Overview

## Architecture Overview

SimpleOS is designed as a minimal, educational operating system that demonstrates fundamental OS concepts. The architecture follows a traditional monolithic kernel design with the following key components:

### 1. Boot Process

```
BIOS → Bootloader → Kernel → Shell
```

- **BIOS**: Loads the bootloader from the first sector of the disk
- **Bootloader**: 512-byte assembly program that loads the kernel
- **Kernel**: Main operating system code written in C
- **Shell**: User interface for interacting with the system

### 2. Memory Layout

```
0x00000000 - 0x0009FFFF: Real mode and BIOS data
0x000A0000 - 0x000BFFFF: Video memory (text mode)
0x000C0000 - 0x000FFFFF: ROM and BIOS
0x00100000 - 0x004FFFFF: Kernel and user space (4MB)
```

### 3. Kernel Architecture

The kernel is organized into several modules:

#### Memory Management
- **Bitmap allocator**: Tracks free/allocated pages
- **Page size**: 4KB
- **Total memory**: 4MB (1024 pages)
- **Allocation strategy**: First-fit

#### Process Management
- **Process table**: Array of process structures
- **Scheduling**: Round-robin (cooperative)
- **Process states**: Ready, Running, Blocked, Terminated
- **Context switching**: Simplified (no register save/restore)

#### File System
- **Structure**: Hierarchical directory tree
- **Storage**: In-memory (not persistent)
- **File types**: Regular files and directories
- **Operations**: Create, read, write, delete, list

#### Device Drivers
- **Keyboard**: PS/2 keyboard with scancode translation
- **Display**: Text mode video memory access
- **System calls**: Interface between user and kernel

### 4. System Call Interface

The kernel provides a simple system call interface:

```c
// System call numbers
#define SYS_WRITE 1    // Write to output
#define SYS_READ 2     // Read from input
#define SYS_EXIT 3     // Terminate process
#define SYS_FORK 4     // Create new process
#define SYS_EXEC 5     // Execute program
```

### 5. Shell Design

The shell provides a command-line interface with:

- **Command parsing**: Space-separated arguments
- **Built-in commands**: help, clear, echo, ls, cd, pwd, exit
- **Command execution**: Direct execution of built-ins
- **Error handling**: Basic error messages

## Design Decisions

### 1. Language Choice

- **Assembly**: Used for bootloader and low-level operations
- **C**: Used for kernel and user programs
- **Rationale**: C provides good control over hardware while being portable

### 2. Memory Management

- **No virtual memory**: Simpler implementation for learning
- **Fixed page size**: 4KB (standard for x86)
- **Bitmap allocation**: Simple and efficient for small systems

### 3. Process Model

- **Cooperative multitasking**: Simpler than preemptive
- **Fixed process limit**: 10 processes maximum
- **No process isolation**: All processes share memory space

### 4. File System

- **In-memory storage**: No disk I/O complexity
- **Simple structure**: Easy to understand and extend
- **No persistence**: Focus on structure rather than storage

### 5. User Interface

- **Text-based shell**: Simple and functional
- **Built-in commands**: No external program loading
- **Basic input/output**: Console-based interaction

## Implementation Details

### Bootloader (bootloader.asm)

```assembly
; Key features:
; - 512 bytes maximum
; - Loads kernel from disk sectors 2-16
; - Jumps to kernel at 0x1000
; - Basic error handling
```

### Kernel (kernel.c)

```c
// Key components:
// - Memory management with bitmap
// - Process table and scheduling
// - System call handler
// - Video memory management
// - Interrupt handling (simplified)
```

### File System (filesystem.c)

```c
// Key structures:
// - file_entry_t: File metadata
// - directory_entry_t: Directory metadata
// - Hierarchical linking with parent/child relationships
```

### Shell (shell.c)

```c
// Key features:
// - Command parsing with strtok()
// - Built-in command dispatch
// - Simple argument handling
// - Error reporting
```

## Limitations and Trade-offs

### Current Limitations

1. **No persistent storage**: File system is in-memory only
2. **Limited memory**: 4MB total system memory
3. **No networking**: No network stack or protocols
4. **No graphics**: Text mode only
5. **No security**: No user accounts or permissions
6. **No real hardware support**: Limited to emulated environment

### Design Trade-offs

1. **Simplicity vs. Features**: Chose simplicity for educational value
2. **Memory vs. Performance**: Fixed memory layout for simplicity
3. **Functionality vs. Complexity**: Basic features to avoid complexity
4. **Portability vs. Optimization**: Focused on x86 for learning

## Future Enhancements

### Short-term Improvements

1. **Persistent file system**: Add disk I/O support
2. **More system calls**: Expand the system call interface
3. **Better error handling**: More robust error reporting
4. **Additional shell commands**: More built-in utilities

### Long-term Goals

1. **Virtual memory**: Implement paging and memory protection
2. **Preemptive multitasking**: Add timer-based scheduling
3. **Device drivers**: Support for real hardware
4. **Network stack**: Basic TCP/IP implementation
5. **User accounts**: Multi-user support
6. **Graphics support**: Simple graphics mode

## Educational Value

This project serves as an excellent learning tool for:

1. **Operating system concepts**: Memory management, process scheduling, file systems
2. **Low-level programming**: Assembly, hardware interaction, system programming
3. **Computer architecture**: x86 architecture, memory layout, I/O operations
4. **Software design**: Modular design, system interfaces, error handling

## Conclusion

SimpleOS demonstrates the fundamental concepts of operating system design in a simple, understandable way. While it lacks many features of modern operating systems, it provides a solid foundation for learning and can be extended with additional functionality as needed.

The modular design makes it easy to understand each component independently, and the simple implementation allows for easy modification and experimentation. This makes it an ideal starting point for anyone interested in operating system development.