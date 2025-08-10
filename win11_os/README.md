# Windows 11-inspired Operating System

A modern, Windows 11-style operating system built from scratch with a graphical user interface, window management, and modern applications.

## 🚀 Features

### Core System
- **Modern Bootloader**: Windows 11-style loading screen with animated progress bar
- **Graphical Kernel**: 640x480 VGA graphics with 256-color support
- **Window Management**: Multi-window support with minimize, maximize, and close
- **Taskbar**: Windows 11-style taskbar with start button and window management
- **Start Menu**: Modern start menu with application grid

### Applications
- **File Explorer**: Complete file management with toolbar, address bar, and file list
- **Settings**: Modern settings interface with categories and controls
- **Desktop**: Icon-based desktop with system folders
- **Context Menus**: Right-click context menus throughout the system

### User Interface
- **Modern Design**: Windows 11-inspired color scheme and styling
- **Window Decorations**: Title bars with minimize, maximize, and close buttons
- **Buttons and Controls**: Modern button styling with hover effects
- **Gradient Backgrounds**: Beautiful gradient desktop backgrounds

### Hardware Support
- **Keyboard**: PS/2 keyboard with scancode translation
- **Mouse**: PS/2 mouse with button and movement support
- **VGA Graphics**: 640x480 resolution with 256 colors
- **System Calls**: Complete system call interface

## 🏗️ Architecture

### Boot Process
```
BIOS → Bootloader → Kernel → GUI → Applications
```

### Memory Layout
```
0x00000000 - 0x0009FFFF: Real mode and BIOS data
0x000A0000 - 0x000BFFFF: Video memory (VGA mode 13h)
0x000C0000 - 0x000FFFFF: ROM and BIOS
0x00100000 - 0x004FFFFF: Kernel and user space (4MB)
```

### System Components
- **Bootloader**: 512-byte x86 assembly with Windows 11 branding
- **Kernel**: C-based kernel with GUI and window management
- **GUI System**: Modern UI components and styling
- **Applications**: File Explorer, Settings, and more
- **Drivers**: Keyboard and mouse drivers

## 🛠️ Building

### Prerequisites

Install the required development tools:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nasm gcc-multilib qemu-system-x86 make

# CentOS/RHEL/Fedora
sudo yum install nasm gcc-multilib qemu-system-x86 make

# macOS (using Homebrew)
brew install nasm gcc qemu make
```

### Build Instructions

1. **Clone and navigate to the project**:
   ```bash
   cd win11_os
   ```

2. **Build the operating system**:
   ```bash
   make all
   ```

3. **Run in QEMU**:
   ```bash
   make run
   ```

### Build Targets

- `make all` - Build the complete OS
- `make clean` - Remove build files
- `make run` - Run OS in QEMU
- `make debug` - Run OS in QEMU with debug support
- `make run-vga` - Run OS with enhanced VGA graphics
- `make install-deps` - Install required packages
- `make docs` - Generate documentation
- `make release` - Create release package

## 🎮 Usage

### Starting the System
1. Run `make run` to start the OS in QEMU
2. The system will boot with a Windows 11-style loading screen
3. The desktop will appear with the taskbar at the bottom

### Using the Interface
- **Start Button**: Click the "Win" button to open the start menu
- **Taskbar**: Shows running applications and allows window switching
- **Windows**: Click and drag title bars to move windows
- **Window Controls**: Use minimize, maximize, and close buttons
- **Right-click**: Context menus for additional options

### Applications

#### File Explorer
- Navigate through folders and files
- Use toolbar buttons for common operations
- View file details in the list view
- Create new folders and manage files

#### Settings
- Browse different setting categories
- Adjust system preferences
- Configure display and personalization
- Manage privacy and account settings

## 📁 Project Structure

```
win11_os/
├── src/
│   ├── boot/
│   │   └── bootloader.asm          # Windows 11-style bootloader
│   ├── kernel/
│   │   └── kernel.c                # Main kernel with GUI
│   ├── gui/
│   │   └── gui_system.c            # Modern GUI components
│   ├── apps/
│   │   ├── file_explorer.c         # File Explorer application
│   │   └── settings.c              # Settings application
│   └── drivers/
│       ├── keyboard.c              # PS/2 keyboard driver
│       └── mouse.c                 # PS/2 mouse driver
├── include/                        # Header files
├── bin/                           # Build output
├── obj/                           # Object files
├── assets/                        # Graphics and resources
├── Makefile                       # Build configuration
├── linker.ld                      # Linker script
└── README.md                      # This file
```

## 🎨 Design Features

### Windows 11 Styling
- **Color Scheme**: Dark blue backgrounds with light gray surfaces
- **Typography**: Clean, modern text rendering
- **Buttons**: Rounded corners with hover effects
- **Windows**: Modern window frames with accent colors
- **Taskbar**: Translucent taskbar with start button

### User Experience
- **Intuitive Navigation**: Familiar Windows-style interface
- **Responsive Design**: Smooth interactions and feedback
- **Consistent Styling**: Unified design language throughout
- **Accessibility**: Clear visual hierarchy and contrast

## 🔧 Development

### Adding New Applications
1. Create a new C file in `src/apps/`
2. Implement the application interface
3. Add to the start menu in the GUI system
4. Update the Makefile to include the new component

### Extending the GUI
1. Add new components to `src/gui/gui_system.c`
2. Implement drawing functions for new elements
3. Add event handling for user interactions
4. Update the kernel to integrate new features

### Customizing the Design
1. Modify color definitions in the GUI system
2. Update window decorations and styling
3. Add new visual effects and animations
4. Customize the desktop background

## 🐛 Debugging

### Debug Mode
Run the OS in debug mode to connect with GDB:

```bash
make debug
```

Then connect GDB:
```bash
gdb -ex "target remote localhost:1234" -ex "symbol-file bin/kernel.bin"
```

### Common Issues
- **Build errors**: Ensure all dependencies are installed
- **Graphics issues**: Try different QEMU display options
- **Input problems**: Check keyboard and mouse configuration
- **Performance**: Adjust QEMU memory and CPU settings

## 📈 Future Enhancements

### Planned Features
- **Network Support**: Basic TCP/IP stack
- **File System**: Persistent storage with disk I/O
- **More Applications**: Calculator, Notepad, Paint
- **Sound Support**: Audio drivers and playback
- **Printing**: Basic printer support

### Advanced Features
- **Virtual Memory**: Paging and memory protection
- **Multi-tasking**: Preemptive process scheduling
- **Graphics Acceleration**: Hardware-accelerated graphics
- **Network Applications**: Web browser, email client
- **Development Tools**: Compiler and debugger

## 🤝 Contributing

This is an educational project designed to demonstrate operating system concepts. Contributions are welcome:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Development Guidelines
- Follow the existing code style
- Add comments for complex logic
- Test on multiple platforms
- Update documentation as needed
- Keep the Windows 11 aesthetic

## 📄 License

This project is provided as educational material. Feel free to use, modify, and learn from it.

## 🙏 Acknowledgments

- **Microsoft Windows 11**: Design inspiration and UI concepts
- **OSDev Community**: Technical guidance and resources
- **QEMU Project**: Emulation platform for testing
- **GNU Toolchain**: Compilation and linking tools

## 📚 Resources

### Learning Materials
- [OSDev Wiki](https://wiki.osdev.org/)
- [Windows 11 Design Guidelines](https://docs.microsoft.com/en-us/windows/apps/design/)
- [x86 Assembly Programming](https://www.nasm.us/)
- [Operating System Concepts](https://www.os-book.com/)

### Related Projects
- [ReactOS](https://reactos.org/) - Windows-compatible OS
- [Haiku](https://www.haiku-os.org/) - BeOS-inspired OS
- [Minix](https://www.minix3.org/) - Educational Unix-like OS

---

**Note**: This is an educational project and not affiliated with Microsoft or Windows. It demonstrates operating system concepts using Windows 11-inspired design elements.