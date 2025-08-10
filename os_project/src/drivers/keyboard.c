#include <stdint.h>
#include <stddef.h>

// Keyboard I/O ports
#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64
#define KEYBOARD_COMMAND_PORT 0x64

// Keyboard commands
#define KEYBOARD_CMD_ENABLE 0xAE
#define KEYBOARD_CMD_DISABLE 0xAD
#define KEYBOARD_CMD_READ_CONFIG 0x20
#define KEYBOARD_CMD_WRITE_CONFIG 0x60

// Keyboard buffer
#define KEYBOARD_BUFFER_SIZE 256

// Global variables
static char keyboard_buffer[KEYBOARD_BUFFER_SIZE];
static int buffer_head = 0;
static int buffer_tail = 0;
static int buffer_count = 0;

// Function declarations
void init_keyboard();
void keyboard_interrupt_handler();
char read_keyboard_char();
int keyboard_buffer_empty();
int keyboard_buffer_full();
void keyboard_send_command(uint8_t command);
uint8_t keyboard_read_data();

// Initialize keyboard
void init_keyboard() {
    // Clear buffer
    for (int i = 0; i < KEYBOARD_BUFFER_SIZE; i++) {
        keyboard_buffer[i] = 0;
    }
    
    buffer_head = 0;
    buffer_tail = 0;
    buffer_count = 0;
    
    // Enable keyboard
    keyboard_send_command(KEYBOARD_CMD_ENABLE);
    
    // Configure keyboard
    keyboard_send_command(KEYBOARD_CMD_READ_CONFIG);
    uint8_t config = keyboard_read_data();
    config |= 0x01;  // Enable interrupt
    config &= ~0x20; // Enable translation
    keyboard_send_command(KEYBOARD_CMD_WRITE_CONFIG);
    keyboard_send_command(config);
}

// Keyboard interrupt handler
void keyboard_interrupt_handler() {
    uint8_t scancode = keyboard_read_data();
    
    // Convert scancode to ASCII (simplified)
    char ascii = 0;
    
    if (scancode < 0x80) {  // Key press (not release)
        switch (scancode) {
            case 0x1C:  // Enter
                ascii = '\n';
                break;
            case 0x0E:  // Backspace
                ascii = '\b';
                break;
            case 0x39:  // Space
                ascii = ' ';
                break;
            default:
                // Simple ASCII conversion for letters and numbers
                if (scancode >= 0x02 && scancode <= 0x0D) {
                    // Numbers 1-0
                    ascii = "1234567890-="[scancode - 0x02];
                } else if (scancode >= 0x10 && scancode <= 0x1B) {
                    // Letters Q-P
                    ascii = "qwertyuiop[]"[scancode - 0x10];
                } else if (scancode >= 0x1E && scancode <= 0x28) {
                    // Letters A-L
                    ascii = "asdfghjkl;'"[scancode - 0x1E];
                } else if (scancode >= 0x2C && scancode <= 0x35) {
                    // Letters Z-M
                    ascii = "zxcvbnm,./"[scancode - 0x2C];
                }
                break;
        }
        
        if (ascii && !keyboard_buffer_full()) {
            keyboard_buffer[buffer_tail] = ascii;
            buffer_tail = (buffer_tail + 1) % KEYBOARD_BUFFER_SIZE;
            buffer_count++;
        }
    }
}

// Read a character from keyboard buffer
char read_keyboard_char() {
    if (keyboard_buffer_empty()) {
        return 0;
    }
    
    char c = keyboard_buffer[buffer_head];
    buffer_head = (buffer_head + 1) % KEYBOARD_BUFFER_SIZE;
    buffer_count--;
    
    return c;
}

// Check if keyboard buffer is empty
int keyboard_buffer_empty() {
    return buffer_count == 0;
}

// Check if keyboard buffer is full
int keyboard_buffer_full() {
    return buffer_count >= KEYBOARD_BUFFER_SIZE;
}

// Send command to keyboard
void keyboard_send_command(uint8_t command) {
    // Wait for input buffer to be empty
    while (__builtin_inb(KEYBOARD_STATUS_PORT) & 0x02);
    __builtin_outb(KEYBOARD_COMMAND_PORT, command);
}

// Read data from keyboard
uint8_t keyboard_read_data() {
    // Wait for output buffer to be full
    while (!(__builtin_inb(KEYBOARD_STATUS_PORT) & 0x01));
    return __builtin_inb(KEYBOARD_DATA_PORT);
}

// Inline assembly functions for I/O
static inline uint8_t __builtin_inb(uint16_t port) {
    uint8_t value;
    __asm__ volatile("inb %1, %0" : "=a"(value) : "Nd"(port));
    return value;
}

static inline void __builtin_outb(uint16_t port, uint8_t value) {
    __asm__ volatile("outb %0, %1" : : "a"(value), "Nd"(port));
}