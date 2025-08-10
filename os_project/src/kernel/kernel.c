#include <stdint.h>
#include <stddef.h>

// Video memory address
#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80
#define WHITE_ON_BLACK 0x0F

// Memory management
#define MEMORY_START 0x100000
#define PAGE_SIZE 4096
#define MAX_PAGES 1024

// Process management
#define MAX_PROCESSES 10
#define PROCESS_STACK_SIZE 4096

// System call numbers
#define SYS_WRITE 1
#define SYS_READ 2
#define SYS_EXIT 3
#define SYS_FORK 4
#define SYS_EXEC 5

// Global variables
static int current_row = 0;
static int current_col = 0;
static uint32_t memory_bitmap[MAX_PAGES / 32];
static int next_pid = 1;

// Process structure
typedef struct {
    int pid;
    int state;  // 0=ready, 1=running, 2=blocked, 3=terminated
    uint32_t stack_ptr;
    uint32_t code_ptr;
    char name[32];
} process_t;

static process_t processes[MAX_PROCESSES];
static int current_process = 0;

// Function declarations
void clear_screen();
void print_char(char c);
void print_string(const char* str);
void print_hex(uint32_t value);
void init_memory();
uint32_t allocate_page();
void free_page(uint32_t page);
void init_processes();
int create_process(const char* name, uint32_t entry_point);
void schedule();
void switch_context(int new_process);
void handle_system_call(uint32_t call_number, uint32_t arg1, uint32_t arg2, uint32_t arg3);

// Initialize the kernel
void kernel_main() {
    clear_screen();
    print_string("SimpleOS Kernel Starting...\n");
    
    init_memory();
    init_processes();
    
    print_string("Memory management initialized\n");
    print_string("Process management initialized\n");
    
    // Create initial shell process
    create_process("shell", 0x2000);
    
    print_string("Kernel initialization complete\n");
    print_string("SimpleOS> ");
    
    // Main kernel loop
    while(1) {
        schedule();
        // Simple round-robin scheduling
        current_process = (current_process + 1) % MAX_PROCESSES;
        if (processes[current_process].state == 1) {
            switch_context(current_process);
        }
    }
}

// Clear the screen
void clear_screen() {
    uint16_t* video_memory = (uint16_t*)VIDEO_MEMORY;
    for (int i = 0; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (WHITE_ON_BLACK << 8) | ' ';
    }
    current_row = 0;
    current_col = 0;
}

// Print a single character
void print_char(char c) {
    if (c == '\n') {
        current_row++;
        current_col = 0;
        if (current_row >= MAX_ROWS) {
            // Scroll screen
            uint16_t* video_memory = (uint16_t*)VIDEO_MEMORY;
            for (int i = 0; i < (MAX_ROWS - 1) * MAX_COLS; i++) {
                video_memory[i] = video_memory[i + MAX_COLS];
            }
            current_row = MAX_ROWS - 1;
        }
        return;
    }
    
    uint16_t* video_memory = (uint16_t*)VIDEO_MEMORY;
    int index = current_row * MAX_COLS + current_col;
    video_memory[index] = (WHITE_ON_BLACK << 8) | c;
    
    current_col++;
    if (current_col >= MAX_COLS) {
        current_col = 0;
        current_row++;
    }
}

// Print a string
void print_string(const char* str) {
    while (*str) {
        print_char(*str);
        str++;
    }
}

// Print hexadecimal value
void print_hex(uint32_t value) {
    char hex_chars[] = "0123456789ABCDEF";
    print_string("0x");
    
    for (int i = 7; i >= 0; i--) {
        uint8_t nibble = (value >> (i * 4)) & 0xF;
        print_char(hex_chars[nibble]);
    }
}

// Initialize memory management
void init_memory() {
    for (int i = 0; i < MAX_PAGES / 32; i++) {
        memory_bitmap[i] = 0;
    }
    // Mark first few pages as used (kernel space)
    memory_bitmap[0] = 0x0000000F;  // First 4 pages used
}

// Allocate a page of memory
uint32_t allocate_page() {
    for (int i = 0; i < MAX_PAGES / 32; i++) {
        if (memory_bitmap[i] != 0xFFFFFFFF) {
            for (int j = 0; j < 32; j++) {
                if (!(memory_bitmap[i] & (1 << j))) {
                    memory_bitmap[i] |= (1 << j);
                    return MEMORY_START + ((i * 32 + j) * PAGE_SIZE);
                }
            }
        }
    }
    return 0;  // No free pages
}

// Free a page of memory
void free_page(uint32_t page) {
    uint32_t page_index = (page - MEMORY_START) / PAGE_SIZE;
    int bitmap_index = page_index / 32;
    int bit_index = page_index % 32;
    memory_bitmap[bitmap_index] &= ~(1 << bit_index);
}

// Initialize process management
void init_processes() {
    for (int i = 0; i < MAX_PROCESSES; i++) {
        processes[i].pid = 0;
        processes[i].state = 0;
        processes[i].stack_ptr = 0;
        processes[i].code_ptr = 0;
        processes[i].name[0] = '\0';
    }
}

// Create a new process
int create_process(const char* name, uint32_t entry_point) {
    for (int i = 0; i < MAX_PROCESSES; i++) {
        if (processes[i].pid == 0) {
            processes[i].pid = next_pid++;
            processes[i].state = 1;  // Ready to run
            processes[i].code_ptr = entry_point;
            processes[i].stack_ptr = allocate_page() + PROCESS_STACK_SIZE;
            
            int j = 0;
            while (name[j] && j < 31) {
                processes[i].name[j] = name[j];
                j++;
            }
            processes[i].name[j] = '\0';
            
            return processes[i].pid;
        }
    }
    return -1;  // No free process slots
}

// Simple scheduler
void schedule() {
    // For now, just a simple round-robin
    // In a real OS, this would be much more sophisticated
}

// Switch to a different process context
void switch_context(int new_process) {
    if (new_process >= 0 && new_process < MAX_PROCESSES) {
        if (processes[new_process].state == 1) {
            current_process = new_process;
            // In a real OS, this would save/restore registers
        }
    }
}

// Handle system calls
void handle_system_call(uint32_t call_number, uint32_t arg1, uint32_t arg2, uint32_t arg3) {
    switch (call_number) {
        case SYS_WRITE:
            print_string((char*)arg1);
            break;
        case SYS_READ:
            // Simple read implementation
            break;
        case SYS_EXIT:
            processes[current_process].state = 3;  // Terminated
            break;
        case SYS_FORK:
            // Fork implementation would go here
            break;
        case SYS_EXEC:
            // Exec implementation would go here
            break;
        default:
            print_string("Unknown system call: ");
            print_hex(call_number);
            print_string("\n");
            break;
    }
}