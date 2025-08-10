#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define MAX_FILES 100
#define MAX_FILENAME 32
#define MAX_FILE_SIZE 4096
#define MAX_DIRECTORIES 50
#define MAX_PATH_LENGTH 128

// File types
#define FILE_TYPE_REGULAR 1
#define FILE_TYPE_DIRECTORY 2

// File permissions
#define PERM_READ 1
#define PERM_WRITE 2
#define PERM_EXECUTE 4

// File system structures
typedef struct {
    char name[MAX_FILENAME];
    uint32_t size;
    uint32_t type;
    uint32_t permissions;
    uint32_t data_start;
    uint32_t parent_dir;
    uint32_t next_file;
} file_entry_t;

typedef struct {
    char name[MAX_FILENAME];
    uint32_t parent_dir;
    uint32_t first_file;
    uint32_t next_dir;
} directory_entry_t;

// Global variables
static file_entry_t file_table[MAX_FILES];
static directory_entry_t directory_table[MAX_DIRECTORIES];
static uint8_t file_data[MAX_FILES * MAX_FILE_SIZE];
static uint32_t next_file_id = 0;
static uint32_t next_dir_id = 0;
static uint32_t current_directory = 0;
static uint32_t data_offset = 0;

// Function declarations
void init_filesystem();
uint32_t create_file(const char* name, uint32_t type, uint32_t permissions);
uint32_t create_directory(const char* name);
int delete_file(uint32_t file_id);
int delete_directory(uint32_t dir_id);
uint32_t find_file(const char* name, uint32_t parent_dir);
uint32_t find_directory(const char* name, uint32_t parent_dir);
int read_file(uint32_t file_id, char* buffer, uint32_t offset, uint32_t size);
int write_file(uint32_t file_id, const char* data, uint32_t offset, uint32_t size);
void list_directory(uint32_t dir_id);
uint32_t get_current_directory();
void set_current_directory(uint32_t dir_id);
char* get_path_string(uint32_t dir_id);

// Initialize the file system
void init_filesystem() {
    // Clear all tables
    memset(file_table, 0, sizeof(file_table));
    memset(directory_table, 0, sizeof(directory_table));
    memset(file_data, 0, sizeof(file_data));
    
    // Create root directory
    strcpy(directory_table[0].name, "/");
    directory_table[0].parent_dir = 0;
    directory_table[0].first_file = 0;
    directory_table[0].next_dir = 0;
    
    next_dir_id = 1;
    next_file_id = 0;
    current_directory = 0;
    data_offset = 0;
    
    // Create some default files
    create_file("kernel.bin", FILE_TYPE_REGULAR, PERM_READ | PERM_EXECUTE);
    create_file("shell.bin", FILE_TYPE_REGULAR, PERM_READ | PERM_EXECUTE);
    create_file("init.bin", FILE_TYPE_REGULAR, PERM_READ | PERM_EXECUTE);
}

// Create a new file
uint32_t create_file(const char* name, uint32_t type, uint32_t permissions) {
    if (next_file_id >= MAX_FILES) {
        return 0xFFFFFFFF;  // Error: no free file slots
    }
    
    uint32_t file_id = next_file_id++;
    
    strncpy(file_table[file_id].name, name, MAX_FILENAME - 1);
    file_table[file_id].name[MAX_FILENAME - 1] = '\0';
    file_table[file_id].size = 0;
    file_table[file_id].type = type;
    file_table[file_id].permissions = permissions;
    file_table[file_id].data_start = data_offset;
    file_table[file_id].parent_dir = current_directory;
    file_table[file_id].next_file = 0;
    
    // Link to directory
    if (directory_table[current_directory].first_file == 0) {
        directory_table[current_directory].first_file = file_id;
    } else {
        // Find last file in directory
        uint32_t last_file = directory_table[current_directory].first_file;
        while (file_table[last_file].next_file != 0) {
            last_file = file_table[last_file].next_file;
        }
        file_table[last_file].next_file = file_id;
    }
    
    data_offset += MAX_FILE_SIZE;
    
    return file_id;
}

// Create a new directory
uint32_t create_directory(const char* name) {
    if (next_dir_id >= MAX_DIRECTORIES) {
        return 0xFFFFFFFF;  // Error: no free directory slots
    }
    
    uint32_t dir_id = next_dir_id++;
    
    strncpy(directory_table[dir_id].name, name, MAX_FILENAME - 1);
    directory_table[dir_id].name[MAX_FILENAME - 1] = '\0';
    directory_table[dir_id].parent_dir = current_directory;
    directory_table[dir_id].first_file = 0;
    directory_table[dir_id].next_dir = 0;
    
    // Link to parent directory
    uint32_t parent = directory_table[current_directory].next_dir;
    if (parent == 0) {
        directory_table[current_directory].next_dir = dir_id;
    } else {
        while (directory_table[parent].next_dir != 0) {
            parent = directory_table[parent].next_dir;
        }
        directory_table[parent].next_dir = dir_id;
    }
    
    return dir_id;
}

// Delete a file
int delete_file(uint32_t file_id) {
    if (file_id >= next_file_id) {
        return -1;  // Invalid file ID
    }
    
    // Remove from directory chain
    uint32_t parent_dir = file_table[file_id].parent_dir;
    uint32_t prev_file = 0;
    uint32_t current_file = directory_table[parent_dir].first_file;
    
    while (current_file != file_id && current_file != 0) {
        prev_file = current_file;
        current_file = file_table[current_file].next_file;
    }
    
    if (current_file == file_id) {
        if (prev_file == 0) {
            directory_table[parent_dir].first_file = file_table[file_id].next_file;
        } else {
            file_table[prev_file].next_file = file_table[file_id].next_file;
        }
    }
    
    // Clear file entry
    memset(&file_table[file_id], 0, sizeof(file_entry_t));
    
    return 0;
}

// Delete a directory
int delete_directory(uint32_t dir_id) {
    if (dir_id >= next_dir_id || dir_id == 0) {
        return -1;  // Invalid directory ID or trying to delete root
    }
    
    // Check if directory is empty
    if (directory_table[dir_id].first_file != 0) {
        return -2;  // Directory not empty
    }
    
    // Remove from parent directory chain
    uint32_t parent_dir = directory_table[dir_id].parent_dir;
    uint32_t prev_dir = 0;
    uint32_t current_dir = directory_table[parent_dir].next_dir;
    
    while (current_dir != dir_id && current_dir != 0) {
        prev_dir = current_dir;
        current_dir = directory_table[current_dir].next_dir;
    }
    
    if (current_dir == dir_id) {
        if (prev_dir == 0) {
            directory_table[parent_dir].next_dir = directory_table[dir_id].next_dir;
        } else {
            directory_table[prev_dir].next_dir = directory_table[dir_id].next_dir;
        }
    }
    
    // Clear directory entry
    memset(&directory_table[dir_id], 0, sizeof(directory_entry_t));
    
    return 0;
}

// Find a file by name in a directory
uint32_t find_file(const char* name, uint32_t parent_dir) {
    uint32_t file_id = directory_table[parent_dir].first_file;
    
    while (file_id != 0) {
        if (strcmp(file_table[file_id].name, name) == 0) {
            return file_id;
        }
        file_id = file_table[file_id].next_file;
    }
    
    return 0xFFFFFFFF;  // File not found
}

// Find a directory by name in a parent directory
uint32_t find_directory(const char* name, uint32_t parent_dir) {
    uint32_t dir_id = directory_table[parent_dir].next_dir;
    
    while (dir_id != 0) {
        if (strcmp(directory_table[dir_id].name, name) == 0) {
            return dir_id;
        }
        dir_id = directory_table[dir_id].next_dir;
    }
    
    return 0xFFFFFFFF;  // Directory not found
}

// Read data from a file
int read_file(uint32_t file_id, char* buffer, uint32_t offset, uint32_t size) {
    if (file_id >= next_file_id) {
        return -1;  // Invalid file ID
    }
    
    if (offset + size > file_table[file_id].size) {
        size = file_table[file_id].size - offset;
    }
    
    if (size > 0) {
        memcpy(buffer, &file_data[file_table[file_id].data_start + offset], size);
    }
    
    return size;
}

// Write data to a file
int write_file(uint32_t file_id, const char* data, uint32_t offset, uint32_t size) {
    if (file_id >= next_file_id) {
        return -1;  // Invalid file ID
    }
    
    if (offset + size > MAX_FILE_SIZE) {
        size = MAX_FILE_SIZE - offset;
    }
    
    if (size > 0) {
        memcpy(&file_data[file_table[file_id].data_start + offset], data, size);
        if (offset + size > file_table[file_id].size) {
            file_table[file_id].size = offset + size;
        }
    }
    
    return size;
}

// List contents of a directory
void list_directory(uint32_t dir_id) {
    if (dir_id >= next_dir_id) {
        return;  // Invalid directory ID
    }
    
    // List files
    uint32_t file_id = directory_table[dir_id].first_file;
    while (file_id != 0) {
        // Print file info (in a real OS, this would use printf)
        // For now, we'll just note that we found files
        file_id = file_table[file_id].next_file;
    }
    
    // List subdirectories
    uint32_t subdir_id = directory_table[dir_id].next_dir;
    while (subdir_id != 0) {
        // Print directory info
        subdir_id = directory_table[subdir_id].next_dir;
    }
}

// Get current directory ID
uint32_t get_current_directory() {
    return current_directory;
}

// Set current directory
void set_current_directory(uint32_t dir_id) {
    if (dir_id < next_dir_id) {
        current_directory = dir_id;
    }
}

// Get path string for a directory
char* get_path_string(uint32_t dir_id) {
    static char path[MAX_PATH_LENGTH];
    char temp_path[MAX_PATH_LENGTH];
    
    path[0] = '\0';
    uint32_t current = dir_id;
    
    while (current != 0) {
        strcpy(temp_path, "/");
        strcat(temp_path, directory_table[current].name);
        strcat(temp_path, path);
        strcpy(path, temp_path);
        current = directory_table[current].parent_dir;
    }
    
    if (path[0] == '\0') {
        strcpy(path, "/");
    }
    
    return path;
}