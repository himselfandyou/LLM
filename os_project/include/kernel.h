#ifndef KERNEL_H
#define KERNEL_H

#include <stdint.h>
#include <stddef.h>

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

// Process states
#define PROCESS_READY 0
#define PROCESS_RUNNING 1
#define PROCESS_BLOCKED 2
#define PROCESS_TERMINATED 3

// Video memory
#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80
#define WHITE_ON_BLACK 0x0F

// Function declarations
void kernel_main();
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

// Process structure
typedef struct {
    int pid;
    int state;
    uint32_t stack_ptr;
    uint32_t code_ptr;
    char name[32];
} process_t;

#endif // KERNEL_H