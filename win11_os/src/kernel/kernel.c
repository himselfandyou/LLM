#include <stdint.h>
#include <stddef.h>
#include <string.h>

// Video memory and display settings
#define VIDEO_MEMORY 0xA0000
#define SCREEN_WIDTH 640
#define SCREEN_HEIGHT 480
#define BYTES_PER_PIXEL 1

// Color definitions (Windows 11 inspired)
#define COLOR_BLACK 0x00
#define COLOR_DARK_BLUE 0x01
#define COLOR_DARK_GREEN 0x02
#define COLOR_DARK_CYAN 0x03
#define COLOR_DARK_RED 0x04
#define COLOR_DARK_MAGENTA 0x05
#define COLOR_DARK_YELLOW 0x06
#define COLOR_LIGHT_GRAY 0x07
#define COLOR_DARK_GRAY 0x08
#define COLOR_BLUE 0x09
#define COLOR_GREEN 0x0A
#define COLOR_CYAN 0x0B
#define COLOR_RED 0x0C
#define COLOR_MAGENTA 0x0D
#define COLOR_YELLOW 0x0E
#define COLOR_WHITE 0x0F

// Window management
#define MAX_WINDOWS 20
#define MAX_WINDOW_TITLE 64
#define TASKBAR_HEIGHT 40
#define START_BUTTON_WIDTH 60

// Window states
#define WINDOW_NORMAL 0
#define WINDOW_MINIMIZED 1
#define WINDOW_MAXIMIZED 2

// Window structure
typedef struct {
    int id;
    int x, y;
    int width, height;
    int state;
    char title[MAX_WINDOW_TITLE];
    uint8_t* buffer;
    int active;
    int visible;
} window_t;

// Taskbar structure
typedef struct {
    int x, y;
    int width, height;
    int start_button_pressed;
    int start_menu_open;
} taskbar_t;

// Global variables
static uint8_t* video_memory = (uint8_t*)VIDEO_MEMORY;
static window_t windows[MAX_WINDOWS];
static int window_count = 0;
static int active_window = -1;
static taskbar_t taskbar;
static int mouse_x = 320, mouse_y = 240;
static int mouse_buttons = 0;

// Function declarations
void kernel_main();
void init_gui();
void init_taskbar();
void draw_desktop();
void draw_taskbar();
void draw_start_button();
void draw_window(window_t* window);
void create_window(int x, int y, int width, int height, const char* title);
void handle_mouse_click(int x, int y, int button);
void handle_keyboard(uint8_t scancode);
void draw_pixel(int x, int y, uint8_t color);
void draw_rectangle(int x, int y, int width, int height, uint8_t color);
void draw_text(int x, int y, const char* text, uint8_t color);
void draw_window_titlebar(window_t* window);
void minimize_window(int window_id);
void maximize_window(int window_id);
void close_window(int window_id);
void bring_window_to_front(int window_id);

// Initialize the kernel
void kernel_main() {
    // Initialize GUI system
    init_gui();
    
    // Initialize taskbar
    init_taskbar();
    
    // Create some example windows
    create_window(100, 100, 300, 200, "File Explorer");
    create_window(150, 150, 250, 180, "Settings");
    create_window(200, 200, 280, 160, "Notepad");
    
    // Main GUI loop
    while(1) {
        // Handle input
        handle_mouse_click(mouse_x, mouse_y, mouse_buttons);
        
        // Redraw everything
        draw_desktop();
        draw_taskbar();
        
        // Draw all windows
        for(int i = 0; i < window_count; i++) {
            if(windows[i].visible) {
                draw_window(&windows[i]);
            }
        }
        
        // Small delay to prevent excessive redrawing
        for(volatile int i = 0; i < 100000; i++);
    }
}

// Initialize GUI system
void init_gui() {
    // Clear video memory
    memset(video_memory, COLOR_DARK_BLUE, SCREEN_WIDTH * SCREEN_HEIGHT);
    
    // Initialize window array
    memset(windows, 0, sizeof(windows));
    window_count = 0;
    active_window = -1;
}

// Initialize taskbar
void init_taskbar() {
    taskbar.x = 0;
    taskbar.y = SCREEN_HEIGHT - TASKBAR_HEIGHT;
    taskbar.width = SCREEN_WIDTH;
    taskbar.height = TASKBAR_HEIGHT;
    taskbar.start_button_pressed = 0;
    taskbar.start_menu_open = 0;
}

// Draw desktop background
void draw_desktop() {
    // Draw gradient background (simplified)
    for(int y = 0; y < SCREEN_HEIGHT - TASKBAR_HEIGHT; y++) {
        uint8_t color = COLOR_DARK_BLUE + (y / 50);
        if(color > COLOR_BLUE) color = COLOR_BLUE;
        
        for(int x = 0; x < SCREEN_WIDTH; x++) {
            draw_pixel(x, y, color);
        }
    }
    
    // Draw some desktop icons (simplified)
    draw_text(50, 50, "This PC", COLOR_WHITE);
    draw_text(50, 80, "Recycle Bin", COLOR_WHITE);
    draw_text(50, 110, "Documents", COLOR_WHITE);
}

// Draw taskbar
void draw_taskbar() {
    // Draw taskbar background
    draw_rectangle(taskbar.x, taskbar.y, taskbar.width, taskbar.height, COLOR_DARK_GRAY);
    
    // Draw start button
    draw_start_button();
    
    // Draw window buttons in taskbar
    int button_x = START_BUTTON_WIDTH + 10;
    for(int i = 0; i < window_count; i++) {
        if(windows[i].visible) {
            // Draw window button
            uint8_t button_color = (i == active_window) ? COLOR_BLUE : COLOR_LIGHT_GRAY;
            draw_rectangle(button_x, taskbar.y + 5, 120, 30, button_color);
            
            // Draw window title (truncated)
            char short_title[16];
            strncpy(short_title, windows[i].title, 15);
            short_title[15] = '\0';
            draw_text(button_x + 5, taskbar.y + 15, short_title, COLOR_BLACK);
            
            button_x += 130;
        }
    }
}

// Draw start button
void draw_start_button() {
    uint8_t button_color = taskbar.start_button_pressed ? COLOR_BLUE : COLOR_DARK_GRAY;
    draw_rectangle(0, taskbar.y, START_BUTTON_WIDTH, taskbar.height, button_color);
    
    // Draw Windows logo (simplified)
    draw_text(10, taskbar.y + 10, "Win", COLOR_WHITE);
}

// Create a new window
void create_window(int x, int y, int width, int height, const char* title) {
    if(window_count >= MAX_WINDOWS) return;
    
    window_t* window = &windows[window_count];
    window->id = window_count;
    window->x = x;
    window->y = y;
    window->width = width;
    window->height = height;
    window->state = WINDOW_NORMAL;
    window->active = 0;
    window->visible = 1;
    
    strncpy(window->title, title, MAX_WINDOW_TITLE - 1);
    window->title[MAX_WINDOW_TITLE - 1] = '\0';
    
    // Allocate window buffer
    window->buffer = (uint8_t*)malloc(width * height);
    if(window->buffer) {
        memset(window->buffer, COLOR_LIGHT_GRAY, width * height);
    }
    
    window_count++;
    
    // Make this window active
    bring_window_to_front(window->id);
}

// Draw a window
void draw_window(window_t* window) {
    if(!window->visible) return;
    
    // Draw window border
    uint8_t border_color = window->active ? COLOR_BLUE : COLOR_DARK_GRAY;
    draw_rectangle(window->x, window->y, window->width, window->height, border_color);
    
    // Draw window background
    draw_rectangle(window->x + 1, window->y + 1, window->width - 2, window->height - 2, COLOR_LIGHT_GRAY);
    
    // Draw title bar
    draw_window_titlebar(window);
    
    // Draw window content (from buffer)
    if(window->buffer) {
        for(int wy = 0; wy < window->height - 20; wy++) {
            for(int wx = 0; wx < window->width - 2; wx++) {
                int screen_x = window->x + 1 + wx;
                int screen_y = window->y + 20 + wy;
                if(screen_x >= 0 && screen_x < SCREEN_WIDTH && screen_y >= 0 && screen_y < SCREEN_HEIGHT - TASKBAR_HEIGHT) {
                    uint8_t pixel = window->buffer[wy * (window->width - 2) + wx];
                    draw_pixel(screen_x, screen_y, pixel);
                }
            }
        }
    }
}

// Draw window title bar
void draw_window_titlebar(window_t* window) {
    uint8_t titlebar_color = window->active ? COLOR_BLUE : COLOR_DARK_GRAY;
    draw_rectangle(window->x, window->y, window->width, 20, titlebar_color);
    
    // Draw title
    draw_text(window->x + 5, window->y + 5, window->title, COLOR_WHITE);
    
    // Draw window controls (minimize, maximize, close)
    int control_x = window->x + window->width - 60;
    
    // Close button
    draw_rectangle(control_x, window->y + 2, 15, 15, COLOR_RED);
    draw_text(control_x + 5, window->y + 5, "X", COLOR_WHITE);
    
    // Maximize button
    control_x -= 20;
    draw_rectangle(control_x, window->y + 2, 15, 15, COLOR_DARK_GRAY);
    draw_text(control_x + 5, window->y + 5, "[]", COLOR_WHITE);
    
    // Minimize button
    control_x -= 20;
    draw_rectangle(control_x, window->y + 2, 15, 15, COLOR_DARK_GRAY);
    draw_text(control_x + 5, window->y + 5, "_", COLOR_WHITE);
}

// Handle mouse clicks
void handle_mouse_click(int x, int y, int button) {
    if(!button) return;
    
    // Check if clicking on taskbar
    if(y >= taskbar.y) {
        // Check start button
        if(x < START_BUTTON_WIDTH) {
            taskbar.start_menu_open = !taskbar.start_menu_open;
            return;
        }
        
        // Check window buttons
        int button_x = START_BUTTON_WIDTH + 10;
        for(int i = 0; i < window_count; i++) {
            if(windows[i].visible) {
                if(x >= button_x && x < button_x + 120 && y >= taskbar.y + 5 && y < taskbar.y + 35) {
                    bring_window_to_front(i);
                    return;
                }
                button_x += 130;
            }
        }
        return;
    }
    
    // Check if clicking on windows
    for(int i = window_count - 1; i >= 0; i--) {
        if(windows[i].visible && x >= windows[i].x && x < windows[i].x + windows[i].width &&
           y >= windows[i].y && y < windows[i].y + windows[i].height) {
            
            bring_window_to_front(i);
            
            // Check window controls
            if(y < windows[i].y + 20) {
                int control_x = windows[i].x + windows[i].width - 60;
                
                // Close button
                if(x >= control_x && x < control_x + 15) {
                    close_window(i);
                    return;
                }
                
                // Maximize button
                control_x -= 20;
                if(x >= control_x && x < control_x + 15) {
                    maximize_window(i);
                    return;
                }
                
                // Minimize button
                control_x -= 20;
                if(x >= control_x && x < control_x + 15) {
                    minimize_window(i);
                    return;
                }
            }
            
            return;
        }
    }
}

// Handle keyboard input
void handle_keyboard(uint8_t scancode) {
    // Handle Alt+Tab (simplified)
    if(scancode == 0x3B) { // F1 key for demo
        // Cycle through windows
        if(window_count > 0) {
            active_window = (active_window + 1) % window_count;
        }
    }
}

// Draw a single pixel
void draw_pixel(int x, int y, uint8_t color) {
    if(x >= 0 && x < SCREEN_WIDTH && y >= 0 && y < SCREEN_HEIGHT) {
        video_memory[y * SCREEN_WIDTH + x] = color;
    }
}

// Draw a rectangle
void draw_rectangle(int x, int y, int width, int height, uint8_t color) {
    for(int py = y; py < y + height; py++) {
        for(int px = x; px < x + width; px++) {
            draw_pixel(px, py, color);
        }
    }
}

// Draw text (simplified - just draws characters as colored rectangles)
void draw_text(int x, int y, const char* text, uint8_t color) {
    int char_x = x;
    while(*text) {
        // Draw a simple character representation
        draw_rectangle(char_x, y, 8, 12, color);
        char_x += 10;
        text++;
    }
}

// Bring window to front
void bring_window_to_front(int window_id) {
    if(window_id < 0 || window_id >= window_count) return;
    
    // Deactivate all windows
    for(int i = 0; i < window_count; i++) {
        windows[i].active = 0;
    }
    
    // Activate the selected window
    windows[window_id].active = 1;
    active_window = window_id;
}

// Minimize window
void minimize_window(int window_id) {
    if(window_id < 0 || window_id >= window_count) return;
    windows[window_id].visible = 0;
}

// Maximize window
void maximize_window(int window_id) {
    if(window_id < 0 || window_id >= window_count) return;
    
    window_t* window = &windows[window_id];
    if(window->state == WINDOW_MAXIMIZED) {
        // Restore
        window->state = WINDOW_NORMAL;
        window->x = 100; // Default position
        window->y = 100;
        window->width = 300; // Default size
        window->height = 200;
    } else {
        // Maximize
        window->state = WINDOW_MAXIMIZED;
        window->x = 0;
        window->y = 0;
        window->width = SCREEN_WIDTH;
        window->height = SCREEN_HEIGHT - TASKBAR_HEIGHT;
    }
}

// Close window
void close_window(int window_id) {
    if(window_id < 0 || window_id >= window_count) return;
    
    // Free window buffer
    if(windows[window_id].buffer) {
        free(windows[window_id].buffer);
    }
    
    // Remove window from array
    for(int i = window_id; i < window_count - 1; i++) {
        windows[i] = windows[i + 1];
        windows[i].id = i;
    }
    
    window_count--;
    
    // Update active window
    if(active_window == window_id) {
        active_window = (window_count > 0) ? 0 : -1;
    } else if(active_window > window_id) {
        active_window--;
    }
}

// Simple memory allocation (for demo purposes)
void* malloc(size_t size) {
    static uint8_t memory_pool[1024*1024]; // 1MB pool
    static size_t pool_used = 0;
    
    if(pool_used + size <= sizeof(memory_pool)) {
        void* ptr = &memory_pool[pool_used];
        pool_used += size;
        return ptr;
    }
    return NULL;
}

// Simple memory deallocation (for demo purposes)
void free(void* ptr) {
    // In a real implementation, this would track and reuse memory
    (void)ptr;
}