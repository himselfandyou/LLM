#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define MAX_COMMAND_LENGTH 256
#define MAX_ARGS 10
#define MAX_PATH_LENGTH 128

// System call numbers
#define SYS_WRITE 1
#define SYS_READ 2
#define SYS_EXIT 3
#define SYS_FORK 4
#define SYS_EXEC 5

// Built-in commands
#define CMD_HELP 0
#define CMD_CLEAR 1
#define CMD_ECHO 2
#define CMD_LS 3
#define CMD_CD 4
#define CMD_PWD 5
#define CMD_EXIT 6

// Global variables
static char current_directory[MAX_PATH_LENGTH] = "/";
static char command_buffer[MAX_COMMAND_LENGTH];
static char* command_args[MAX_ARGS];

// Function declarations
void shell_main();
void print_prompt();
void read_command();
void parse_command();
int execute_command();
int execute_builtin(int cmd);
void print_help();
void clear_screen();
void echo_command();
void list_files();
void change_directory();
void print_working_directory();
void system_call(uint32_t call_number, uint32_t arg1, uint32_t arg2, uint32_t arg3);

// Main shell function
void shell_main() {
    print_string("SimpleOS Shell v1.0\n");
    print_string("Type 'help' for available commands\n\n");
    
    while(1) {
        print_prompt();
        read_command();
        parse_command();
        execute_command();
    }
}

// Print shell prompt
void print_prompt() {
    print_string("SimpleOS");
    print_string(current_directory);
    print_string("> ");
}

// Read command from user
void read_command() {
    int i = 0;
    char c;
    
    while(i < MAX_COMMAND_LENGTH - 1) {
        // In a real OS, this would read from keyboard
        // For now, we'll simulate with a simple input
        c = get_char();  // This would be implemented in the kernel
        
        if(c == '\n' || c == '\r') {
            break;
        }
        
        command_buffer[i++] = c;
    }
    
    command_buffer[i] = '\0';
}

// Parse command into arguments
void parse_command() {
    char* token;
    int arg_count = 0;
    
    // Reset arguments
    for(int i = 0; i < MAX_ARGS; i++) {
        command_args[i] = NULL;
    }
    
    // Split command by spaces
    token = strtok(command_buffer, " ");
    while(token != NULL && arg_count < MAX_ARGS - 1) {
        command_args[arg_count++] = token;
        token = strtok(NULL, " ");
    }
    
    command_args[arg_count] = NULL;
}

// Execute the parsed command
int execute_command() {
    if(command_args[0] == NULL) {
        return 0;  // Empty command
    }
    
    // Check for built-in commands
    if(strcmp(command_args[0], "help") == 0) {
        return execute_builtin(CMD_HELP);
    }
    else if(strcmp(command_args[0], "clear") == 0) {
        return execute_builtin(CMD_CLEAR);
    }
    else if(strcmp(command_args[0], "echo") == 0) {
        return execute_builtin(CMD_ECHO);
    }
    else if(strcmp(command_args[0], "ls") == 0) {
        return execute_builtin(CMD_LS);
    }
    else if(strcmp(command_args[0], "cd") == 0) {
        return execute_builtin(CMD_CD);
    }
    else if(strcmp(command_args[0], "pwd") == 0) {
        return execute_builtin(CMD_PWD);
    }
    else if(strcmp(command_args[0], "exit") == 0) {
        return execute_builtin(CMD_EXIT);
    }
    else {
        // Try to execute as external command
        print_string("Command not found: ");
        print_string(command_args[0]);
        print_string("\n");
        return -1;
    }
}

// Execute built-in commands
int execute_builtin(int cmd) {
    switch(cmd) {
        case CMD_HELP:
            print_help();
            break;
        case CMD_CLEAR:
            clear_screen();
            break;
        case CMD_ECHO:
            echo_command();
            break;
        case CMD_LS:
            list_files();
            break;
        case CMD_CD:
            change_directory();
            break;
        case CMD_PWD:
            print_working_directory();
            break;
        case CMD_EXIT:
            system_call(SYS_EXIT, 0, 0, 0);
            break;
        default:
            print_string("Unknown built-in command\n");
            return -1;
    }
    return 0;
}

// Print help information
void print_help() {
    print_string("Available commands:\n");
    print_string("  help     - Show this help message\n");
    print_string("  clear    - Clear the screen\n");
    print_string("  echo     - Print arguments\n");
    print_string("  ls       - List files in current directory\n");
    print_string("  cd       - Change directory\n");
    print_string("  pwd      - Print working directory\n");
    print_string("  exit     - Exit the shell\n");
    print_string("\n");
}

// Clear the screen
void clear_screen() {
    // This would call the kernel's clear screen function
    system_call(SYS_WRITE, (uint32_t)"\033[2J", 0, 0);
}

// Echo command implementation
void echo_command() {
    for(int i = 1; command_args[i] != NULL; i++) {
        print_string(command_args[i]);
        print_string(" ");
    }
    print_string("\n");
}

// List files (simplified)
void list_files() {
    print_string("Directory listing for: ");
    print_string(current_directory);
    print_string("\n");
    print_string("  .\n");
    print_string("  ..\n");
    print_string("  kernel.bin\n");
    print_string("  shell.bin\n");
    print_string("  init.bin\n");
    print_string("\n");
}

// Change directory
void change_directory() {
    if(command_args[1] == NULL) {
        strcpy(current_directory, "/");
    }
    else if(strcmp(command_args[1], "..") == 0) {
        // Go to parent directory
        char* last_slash = strrchr(current_directory, '/');
        if(last_slash != current_directory) {
            *last_slash = '\0';
        }
    }
    else if(strcmp(command_args[1], ".") == 0) {
        // Stay in current directory
        return;
    }
    else {
        // Change to specified directory
        if(strlen(current_directory) + strlen(command_args[1]) + 2 < MAX_PATH_LENGTH) {
            if(current_directory[strlen(current_directory) - 1] != '/') {
                strcat(current_directory, "/");
            }
            strcat(current_directory, command_args[1]);
        }
    }
}

// Print working directory
void print_working_directory() {
    print_string(current_directory);
    print_string("\n");
}

// Make system call
void system_call(uint32_t call_number, uint32_t arg1, uint32_t arg2, uint32_t arg3) {
    // This would be implemented in assembly to make actual system calls
    // For now, it's a placeholder
}

// Helper functions (these would be provided by the kernel)
void print_string(const char* str) {
    system_call(SYS_WRITE, (uint32_t)str, 0, 0);
}

char get_char() {
    // This would read from keyboard buffer
    // For now, return a dummy character
    return 'a';
}