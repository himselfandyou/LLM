#include <stdint.h>
#include <stddef.h>
#include <string.h>

// File Explorer for Windows 11-inspired OS
// This provides a modern file management interface

// File types
#define FILE_TYPE_FOLDER 0
#define FILE_TYPE_DOCUMENT 1
#define FILE_TYPE_IMAGE 2
#define FILE_TYPE_APPLICATION 3
#define FILE_TYPE_UNKNOWN 4

// File entry structure
typedef struct {
    char name[64];
    char extension[8];
    int type;
    uint32_t size;
    int selected;
} file_entry_t;

// File Explorer window structure
typedef struct {
    int x, y;
    int width, height;
    int visible;
    char current_path[256];
    file_entry_t files[100];
    int file_count;
    int scroll_offset;
    int selected_file;
} file_explorer_t;

// Global File Explorer instance
static file_explorer_t file_explorer;

// Function declarations
void init_file_explorer();
void draw_file_explorer();
void create_file_explorer_window();
void draw_file_list();
void draw_address_bar();
void draw_toolbar();
void draw_status_bar();
void handle_file_explorer_click(int x, int y);
void navigate_to_folder(const char* path);
void select_file(int index);
void open_file(int index);
void create_new_folder();
void delete_selected_file();
void refresh_file_list();
void populate_sample_files();

// Initialize File Explorer
void init_file_explorer() {
    file_explorer.x = 100;
    file_explorer.y = 100;
    file_explorer.width = 600;
    file_explorer.height = 400;
    file_explorer.visible = 0;
    file_explorer.scroll_offset = 0;
    file_explorer.selected_file = -1;
    
    strcpy(file_explorer.current_path, "C:\\");
    
    // Populate with sample files
    populate_sample_files();
}

// Create File Explorer window
void create_file_explorer_window() {
    file_explorer.visible = 1;
    file_explorer.x = 100;
    file_explorer.y = 100;
}

// Draw File Explorer
void draw_file_explorer() {
    if(!file_explorer.visible) return;
    
    // Draw window frame
    draw_modern_window_frame(file_explorer.x, file_explorer.y, 
                           file_explorer.width, file_explorer.height, "File Explorer");
    
    // Draw toolbar
    draw_toolbar();
    
    // Draw address bar
    draw_address_bar();
    
    // Draw file list
    draw_file_list();
    
    // Draw status bar
    draw_status_bar();
}

// Draw toolbar
void draw_toolbar() {
    int toolbar_y = file_explorer.y + 30;
    
    // Draw toolbar background
    draw_rectangle(file_explorer.x, toolbar_y, file_explorer.width, 30, 0x07);
    
    // Draw toolbar buttons
    int button_x = file_explorer.x + 10;
    
    // Back button
    draw_rectangle(button_x, toolbar_y + 5, 60, 20, 0x08);
    draw_text(button_x + 5, toolbar_y + 10, "Back", 0x0F);
    button_x += 70;
    
    // Forward button
    draw_rectangle(button_x, toolbar_y + 5, 60, 20, 0x08);
    draw_text(button_x + 5, toolbar_y + 10, "Forward", 0x0F);
    button_x += 70;
    
    // Up button
    draw_rectangle(button_x, toolbar_y + 5, 60, 20, 0x08);
    draw_text(button_x + 5, toolbar_y + 10, "Up", 0x0F);
    button_x += 70;
    
    // New folder button
    draw_rectangle(button_x, toolbar_y + 5, 80, 20, 0x08);
    draw_text(button_x + 5, toolbar_y + 10, "New Folder", 0x0F);
    button_x += 90;
    
    // Refresh button
    draw_rectangle(button_x, toolbar_y + 5, 60, 20, 0x08);
    draw_text(button_x + 5, toolbar_y + 10, "Refresh", 0x0F);
}

// Draw address bar
void draw_address_bar() {
    int address_y = file_explorer.y + 60;
    
    // Draw address bar background
    draw_rectangle(file_explorer.x, address_y, file_explorer.width, 25, 0x0F);
    
    // Draw address text
    draw_text(file_explorer.x + 5, address_y + 5, "Address: ", 0x00);
    draw_text(file_explorer.x + 60, address_y + 5, file_explorer.current_path, 0x00);
}

// Draw file list
void draw_file_list() {
    int list_y = file_explorer.y + 85;
    int list_height = file_explorer.height - 120;
    
    // Draw list background
    draw_rectangle(file_explorer.x, list_y, file_explorer.width, list_height, 0x0F);
    
    // Draw column headers
    int header_y = list_y;
    draw_rectangle(file_explorer.x, header_y, file_explorer.width, 20, 0x08);
    draw_text(file_explorer.x + 5, header_y + 5, "Name", 0x0F);
    draw_text(file_explorer.x + 300, header_y + 5, "Type", 0x0F);
    draw_text(file_explorer.x + 400, header_y + 5, "Size", 0x0F);
    
    // Draw file entries
    int entry_y = header_y + 20;
    int visible_entries = (list_height - 20) / 20;
    
    for(int i = 0; i < visible_entries && i + file_explorer.scroll_offset < file_explorer.file_count; i++) {
        int file_index = i + file_explorer.scroll_offset;
        file_entry_t* file = &file_explorer.files[file_index];
        
        // Draw selection background
        uint8_t bg_color = (file_index == file_explorer.selected_file) ? 0x09 : 0x0F;
        draw_rectangle(file_explorer.x, entry_y, file_explorer.width, 20, bg_color);
        
        // Draw file icon (simplified)
        char icon[4] = "  ";
        switch(file->type) {
            case FILE_TYPE_FOLDER:
                icon[0] = '[';
                icon[1] = ']';
                break;
            case FILE_TYPE_DOCUMENT:
                icon[0] = 'D';
                break;
            case FILE_TYPE_IMAGE:
                icon[0] = 'I';
                break;
            case FILE_TYPE_APPLICATION:
                icon[0] = 'A';
                break;
            default:
                icon[0] = '?';
                break;
        }
        
        // Draw file name
        draw_text(file_explorer.x + 5, entry_y + 5, icon, 0x00);
        draw_text(file_explorer.x + 25, entry_y + 5, file->name, 0x00);
        
        // Draw file type
        char type_text[16];
        switch(file->type) {
            case FILE_TYPE_FOLDER:
                strcpy(type_text, "Folder");
                break;
            case FILE_TYPE_DOCUMENT:
                strcpy(type_text, "Document");
                break;
            case FILE_TYPE_IMAGE:
                strcpy(type_text, "Image");
                break;
            case FILE_TYPE_APPLICATION:
                strcpy(type_text, "Application");
                break;
            default:
                strcpy(type_text, "Unknown");
                break;
        }
        draw_text(file_explorer.x + 300, entry_y + 5, type_text, 0x00);
        
        // Draw file size
        if(file->type == FILE_TYPE_FOLDER) {
            draw_text(file_explorer.x + 400, entry_y + 5, "<DIR>", 0x00);
        } else {
            char size_text[16];
            if(file->size < 1024) {
                sprintf(size_text, "%d B", file->size);
            } else if(file->size < 1024*1024) {
                sprintf(size_text, "%d KB", file->size / 1024);
            } else {
                sprintf(size_text, "%d MB", file->size / (1024*1024));
            }
            draw_text(file_explorer.x + 400, entry_y + 5, size_text, 0x00);
        }
        
        entry_y += 20;
    }
}

// Draw status bar
void draw_status_bar() {
    int status_y = file_explorer.y + file_explorer.height - 25;
    
    // Draw status bar background
    draw_rectangle(file_explorer.x, status_y, file_explorer.width, 25, 0x08);
    
    // Draw status text
    char status_text[128];
    if(file_explorer.selected_file >= 0) {
        sprintf(status_text, "Selected: %s", file_explorer.files[file_explorer.selected_file].name);
    } else {
        sprintf(status_text, "%d items", file_explorer.file_count);
    }
    draw_text(file_explorer.x + 5, status_y + 5, status_text, 0x0F);
}

// Handle File Explorer clicks
void handle_file_explorer_click(int x, int y) {
    if(!file_explorer.visible) return;
    
    // Check if click is within window bounds
    if(x < file_explorer.x || x > file_explorer.x + file_explorer.width ||
       y < file_explorer.y || y > file_explorer.y + file_explorer.height) {
        return;
    }
    
    // Convert to window coordinates
    int wx = x - file_explorer.x;
    int wy = y - file_explorer.y;
    
    // Check toolbar clicks
    if(wy >= 30 && wy < 60) {
        int button_x = 10;
        
        // Back button
        if(wx >= button_x && wx < button_x + 60) {
            // Navigate back
            return;
        }
        button_x += 70;
        
        // Forward button
        if(wx >= button_x && wx < button_x + 60) {
            // Navigate forward
            return;
        }
        button_x += 70;
        
        // Up button
        if(wx >= button_x && wx < button_x + 60) {
            // Navigate up
            return;
        }
        button_x += 70;
        
        // New folder button
        if(wx >= button_x && wx < button_x + 80) {
            create_new_folder();
            return;
        }
        button_x += 90;
        
        // Refresh button
        if(wx >= button_x && wx < button_x + 60) {
            refresh_file_list();
            return;
        }
    }
    
    // Check file list clicks
    if(wy >= 85 && wy < file_explorer.height - 25) {
        int list_y = wy - 85;
        if(list_y >= 20) { // Skip header
            int file_index = (list_y - 20) / 20 + file_explorer.scroll_offset;
            if(file_index < file_explorer.file_count) {
                select_file(file_index);
                
                // Double-click to open
                if(list_y % 20 < 10) { // Simplified double-click detection
                    open_file(file_index);
                }
            }
        }
    }
}

// Navigate to folder
void navigate_to_folder(const char* path) {
    strcpy(file_explorer.current_path, path);
    refresh_file_list();
}

// Select file
void select_file(int index) {
    if(index >= 0 && index < file_explorer.file_count) {
        file_explorer.selected_file = index;
    }
}

// Open file
void open_file(int index) {
    if(index < 0 || index >= file_explorer.file_count) return;
    
    file_entry_t* file = &file_explorer.files[index];
    
    if(file->type == FILE_TYPE_FOLDER) {
        // Navigate into folder
        char new_path[256];
        sprintf(new_path, "%s%s\\", file_explorer.current_path, file->name);
        navigate_to_folder(new_path);
    } else {
        // Open file (would launch appropriate application)
        // For now, just show a message
        // In a real implementation, this would launch the associated app
    }
}

// Create new folder
void create_new_folder() {
    // In a real implementation, this would prompt for folder name
    // and create the folder in the file system
    // For now, just add to the list
    if(file_explorer.file_count < 100) {
        file_entry_t* new_folder = &file_explorer.files[file_explorer.file_count];
        strcpy(new_folder->name, "New Folder");
        strcpy(new_folder->extension, "");
        new_folder->type = FILE_TYPE_FOLDER;
        new_folder->size = 0;
        new_folder->selected = 0;
        file_explorer.file_count++;
    }
}

// Delete selected file
void delete_selected_file() {
    if(file_explorer.selected_file >= 0 && file_explorer.selected_file < file_explorer.file_count) {
        // Remove file from list
        for(int i = file_explorer.selected_file; i < file_explorer.file_count - 1; i++) {
            file_explorer.files[i] = file_explorer.files[i + 1];
        }
        file_explorer.file_count--;
        file_explorer.selected_file = -1;
    }
}

// Refresh file list
void refresh_file_list() {
    // In a real implementation, this would read the actual file system
    // For now, just repopulate with sample files
    populate_sample_files();
}

// Populate with sample files
void populate_sample_files() {
    file_explorer.file_count = 0;
    
    // Add some sample folders
    strcpy(file_explorer.files[file_explorer.file_count].name, "Documents");
    strcpy(file_explorer.files[file_explorer.file_count].extension, "");
    file_explorer.files[file_explorer.file_count].type = FILE_TYPE_FOLDER;
    file_explorer.files[file_explorer.file_count].size = 0;
    file_explorer.files[file_explorer.file_count].selected = 0;
    file_explorer.file_count++;
    
    strcpy(file_explorer.files[file_explorer.file_count].name, "Pictures");
    strcpy(file_explorer.files[file_explorer.file_count].extension, "");
    file_explorer.files[file_explorer.file_count].type = FILE_TYPE_FOLDER;
    file_explorer.files[file_explorer.file_count].size = 0;
    file_explorer.files[file_explorer.file_count].selected = 0;
    file_explorer.file_count++;
    
    strcpy(file_explorer.files[file_explorer.file_count].name, "Music");
    strcpy(file_explorer.files[file_explorer.file_count].extension, "");
    file_explorer.files[file_explorer.file_count].type = FILE_TYPE_FOLDER;
    file_explorer.files[file_explorer.file_count].size = 0;
    file_explorer.files[file_explorer.file_count].selected = 0;
    file_explorer.file_count++;
    
    // Add some sample files
    strcpy(file_explorer.files[file_explorer.file_count].name, "readme");
    strcpy(file_explorer.files[file_explorer.file_count].extension, "txt");
    file_explorer.files[file_explorer.file_count].type = FILE_TYPE_DOCUMENT;
    file_explorer.files[file_explorer.file_count].size = 1024;
    file_explorer.files[file_explorer.file_count].selected = 0;
    file_explorer.file_count++;
    
    strcpy(file_explorer.files[file_explorer.file_count].name, "screenshot");
    strcpy(file_explorer.files[file_explorer.file_count].extension, "png");
    file_explorer.files[file_explorer.file_count].type = FILE_TYPE_IMAGE;
    file_explorer.files[file_explorer.file_count].size = 2048576;
    file_explorer.files[file_explorer.file_count].selected = 0;
    file_explorer.file_count++;
    
    strcpy(file_explorer.files[file_explorer.file_count].name, "calculator");
    strcpy(file_explorer.files[file_explorer.file_count].extension, "exe");
    file_explorer.files[file_explorer.file_count].type = FILE_TYPE_APPLICATION;
    file_explorer.files[file_explorer.file_count].size = 512000;
    file_explorer.files[file_explorer.file_count].selected = 0;
    file_explorer.file_count++;
}

// Helper functions (these would be implemented in the kernel)
void draw_modern_window_frame(int x, int y, int width, int height, const char* title) {
    // This would be implemented in the kernel
    (void)x; (void)y; (void)width; (void)height; (void)title;
}

void draw_rectangle(int x, int y, int width, int height, uint8_t color) {
    // This would be implemented in the kernel
    (void)x; (void)y; (void)width; (void)height; (void)color;
}

void draw_text(int x, int y, const char* text, uint8_t color) {
    // This would be implemented in the kernel
    (void)x; (void)y; (void)text; (void)color;
}

int sprintf(char* str, const char* format, ...) {
    // Simplified sprintf implementation
    // In a real implementation, this would handle format strings
    strcpy(str, format);
    return strlen(str);
}