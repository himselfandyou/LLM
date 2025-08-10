#include <stdint.h>
#include <stddef.h>

// Mouse I/O ports
#define MOUSE_DATA_PORT 0x60
#define MOUSE_STATUS_PORT 0x64
#define MOUSE_COMMAND_PORT 0x64

// Mouse commands
#define MOUSE_CMD_ENABLE 0xA8
#define MOUSE_CMD_DISABLE 0xA7
#define MOUSE_CMD_READ_CONFIG 0x20
#define MOUSE_CMD_WRITE_CONFIG 0x60
#define MOUSE_CMD_SET_DEFAULTS 0xF6
#define MOUSE_CMD_ENABLE_STREAMING 0xF4

// Mouse packet structure
typedef struct {
    uint8_t buttons;
    int8_t x_movement;
    int8_t y_movement;
    int8_t z_movement;
} mouse_packet_t;

// Mouse state
typedef struct {
    int x, y;
    int buttons;
    int packet_byte;
    uint8_t packet_data[3];
    int packet_ready;
} mouse_state_t;

// Global variables
static mouse_state_t mouse_state;
static mouse_packet_t current_packet;

// Function declarations
void init_mouse();
void mouse_interrupt_handler();
void mouse_send_command(uint8_t command);
uint8_t mouse_read_data();
void mouse_set_position(int x, int y);
void mouse_get_position(int* x, int* y);
int mouse_get_buttons();
void mouse_process_packet();

// Initialize mouse
void init_mouse() {
    // Initialize mouse state
    mouse_state.x = 320;  // Center of screen
    mouse_state.y = 240;
    mouse_state.buttons = 0;
    mouse_state.packet_byte = 0;
    mouse_state.packet_ready = 0;
    
    // Clear packet data
    for(int i = 0; i < 3; i++) {
        mouse_state.packet_data[i] = 0;
    }
    
    // Enable mouse
    mouse_send_command(MOUSE_CMD_ENABLE);
    
    // Configure mouse
    mouse_send_command(MOUSE_CMD_READ_CONFIG);
    uint8_t config = mouse_read_data();
    config |= 0x02;  // Enable mouse interrupt
    config &= ~0x20; // Enable translation
    mouse_send_command(MOUSE_CMD_WRITE_CONFIG);
    mouse_send_command(config);
    
    // Set mouse defaults
    mouse_send_command(MOUSE_CMD_SET_DEFAULTS);
    mouse_read_data();  // Read ACK
    
    // Enable streaming
    mouse_send_command(MOUSE_CMD_ENABLE_STREAMING);
    mouse_read_data();  // Read ACK
}

// Mouse interrupt handler
void mouse_interrupt_handler() {
    uint8_t data = mouse_read_data();
    
    // Store packet data
    mouse_state.packet_data[mouse_state.packet_byte] = data;
    mouse_state.packet_byte++;
    
    // Check if we have a complete packet (3 bytes)
    if(mouse_state.packet_byte >= 3) {
        mouse_process_packet();
        mouse_state.packet_byte = 0;
    }
}

// Process mouse packet
void mouse_process_packet() {
    uint8_t* packet = mouse_state.packet_data;
    
    // Extract button states
    current_packet.buttons = packet[0] & 0x07;
    
    // Extract movement (sign-extend 9-bit values)
    current_packet.x_movement = (int8_t)(packet[1]);
    current_packet.y_movement = (int8_t)(packet[2]);
    
    // Update mouse position
    mouse_state.x += current_packet.x_movement;
    mouse_state.y -= current_packet.y_movement;  // Invert Y axis
    
    // Clamp to screen boundaries
    if(mouse_state.x < 0) mouse_state.x = 0;
    if(mouse_state.x >= 640) mouse_state.x = 639;
    if(mouse_state.y < 0) mouse_state.y = 0;
    if(mouse_state.y >= 480) mouse_state.y = 479;
    
    // Update button state
    mouse_state.buttons = current_packet.buttons;
    
    // Mark packet as ready
    mouse_state.packet_ready = 1;
}

// Send command to mouse
void mouse_send_command(uint8_t command) {
    // Wait for input buffer to be empty
    while (__builtin_inb(MOUSE_STATUS_PORT) & 0x02);
    __builtin_outb(MOUSE_COMMAND_PORT, command);
}

// Read data from mouse
uint8_t mouse_read_data() {
    // Wait for output buffer to be full
    while (!(__builtin_inb(MOUSE_STATUS_PORT) & 0x01));
    return __builtin_inb(MOUSE_DATA_PORT);
}

// Set mouse position
void mouse_set_position(int x, int y) {
    if(x >= 0 && x < 640 && y >= 0 && y < 480) {
        mouse_state.x = x;
        mouse_state.y = y;
    }
}

// Get mouse position
void mouse_get_position(int* x, int* y) {
    *x = mouse_state.x;
    *y = mouse_state.y;
}

// Get mouse buttons
int mouse_get_buttons() {
    return mouse_state.buttons;
}

// Check if mouse packet is ready
int mouse_packet_ready() {
    return mouse_state.packet_ready;
}

// Get current mouse packet
mouse_packet_t* mouse_get_packet() {
    if(mouse_state.packet_ready) {
        mouse_state.packet_ready = 0;
        return &current_packet;
    }
    return NULL;
}

// Check if left button is pressed
int mouse_left_button_pressed() {
    return (mouse_state.buttons & 0x01) != 0;
}

// Check if right button is pressed
int mouse_right_button_pressed() {
    return (mouse_state.buttons & 0x02) != 0;
}

// Check if middle button is pressed
int mouse_middle_button_pressed() {
    return (mouse_state.buttons & 0x04) != 0;
}

// Get mouse movement since last call
void mouse_get_movement(int* dx, int* dy) {
    *dx = current_packet.x_movement;
    *dy = -current_packet.y_movement;  // Invert Y axis
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