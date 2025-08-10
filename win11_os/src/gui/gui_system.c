#include <stdint.h>
#include <stddef.h>
#include <string.h>

// GUI System for Windows 11-inspired OS
// This provides modern UI components and styling

// Color palette (Windows 11 inspired)
#define WIN11_ACCENT_COLOR 0x09      // Blue
#define WIN11_BACKGROUND_COLOR 0x01  // Dark blue
#define WIN11_SURFACE_COLOR 0x07     // Light gray
#define WIN11_TEXT_COLOR 0x0F        // White
#define WIN11_BORDER_COLOR 0x08      // Dark gray
#define WIN11_HOVER_COLOR 0x0B       // Light blue
#define WIN11_ACTIVE_COLOR 0x0C      // Red

// Component types
#define COMPONENT_BUTTON 1
#define COMPONENT_MENU 2
#define COMPONENT_WINDOW 3
#define COMPONENT_TASKBAR 4
#define COMPONENT_START_MENU 5

// Button states
#define BUTTON_NORMAL 0
#define BUTTON_HOVER 1
#define BUTTON_PRESSED 2
#define BUTTON_DISABLED 3

// Menu structure
typedef struct {
    int x, y;
    int width, height;
    int visible;
    char items[10][32];
    int item_count;
    int selected_item;
} menu_t;

// Button structure
typedef struct {
    int x, y;
    int width, height;
    char text[32];
    int state;
    int (*on_click)(void);
} button_t;

// Start menu structure
typedef struct {
    int x, y;
    int width, height;
    int visible;
    button_t apps[20];
    int app_count;
} start_menu_t;

// Global GUI components
static start_menu_t start_menu;
static menu_t context_menu;
static button_t taskbar_buttons[10];
static int taskbar_button_count = 0;

// Function declarations
void init_gui_system();
void draw_modern_button(button_t* button);
void draw_start_menu();
void draw_context_menu();
void draw_modern_window_frame(int x, int y, int width, int height, const char* title);
void draw_rounded_rectangle(int x, int y, int width, int height, uint8_t color);
void draw_gradient_background();
void draw_modern_taskbar();
void create_start_menu();
void add_start_menu_app(const char* name, int (*app_launcher)(void));
void show_context_menu(int x, int y);
void hide_context_menu();
int handle_gui_click(int x, int y);

// Initialize GUI system
void init_gui_system() {
    // Initialize start menu
    create_start_menu();
    
    // Initialize context menu
    context_menu.x = 0;
    context_menu.y = 0;
    context_menu.width = 200;
    context_menu.height = 150;
    context_menu.visible = 0;
    context_menu.item_count = 0;
    context_menu.selected_item = -1;
    
    // Add some context menu items
    strcpy(context_menu.items[context_menu.item_count++], "New");
    strcpy(context_menu.items[context_menu.item_count++], "Open");
    strcpy(context_menu.items[context_menu.item_count++], "Save");
    strcpy(context_menu.items[context_menu.item_count++], "Properties");
    
    // Initialize taskbar buttons
    taskbar_button_count = 0;
}

// Create start menu
void create_start_menu() {
    start_menu.x = 0;
    start_menu.y = 440; // Above taskbar
    start_menu.width = 300;
    start_menu.height = 400;
    start_menu.visible = 0;
    start_menu.app_count = 0;
    
    // Add some default apps
    add_start_menu_app("File Explorer", NULL);
    add_start_menu_app("Settings", NULL);
    add_start_menu_app("Notepad", NULL);
    add_start_menu_app("Calculator", NULL);
    add_start_menu_app("Paint", NULL);
    add_start_menu_app("Terminal", NULL);
}

// Add app to start menu
void add_start_menu_app(const char* name, int (*app_launcher)(void)) {
    if(start_menu.app_count >= 20) return;
    
    button_t* app = &start_menu.apps[start_menu.app_count];
    strcpy(app->text, name);
    app->x = 10;
    app->y = 10 + (start_menu.app_count * 40);
    app->width = 280;
    app->height = 35;
    app->state = BUTTON_NORMAL;
    app->on_click = app_launcher;
    
    start_menu.app_count++;
}

// Draw modern button with Windows 11 styling
void draw_modern_button(button_t* button) {
    uint8_t bg_color, border_color, text_color;
    
    // Determine colors based on state
    switch(button->state) {
        case BUTTON_NORMAL:
            bg_color = WIN11_SURFACE_COLOR;
            border_color = WIN11_BORDER_COLOR;
            text_color = WIN11_TEXT_COLOR;
            break;
        case BUTTON_HOVER:
            bg_color = WIN11_HOVER_COLOR;
            border_color = WIN11_ACCENT_COLOR;
            text_color = WIN11_TEXT_COLOR;
            break;
        case BUTTON_PRESSED:
            bg_color = WIN11_ACCENT_COLOR;
            border_color = WIN11_ACCENT_COLOR;
            text_color = WIN11_TEXT_COLOR;
            break;
        case BUTTON_DISABLED:
            bg_color = WIN11_BORDER_COLOR;
            border_color = WIN11_BORDER_COLOR;
            text_color = WIN11_BORDER_COLOR;
            break;
    }
    
    // Draw button background with rounded corners
    draw_rounded_rectangle(button->x, button->y, button->width, button->height, bg_color);
    
    // Draw border
    draw_rectangle(button->x, button->y, button->width, 1, border_color);
    draw_rectangle(button->x, button->y, 1, button->height, border_color);
    draw_rectangle(button->x + button->width - 1, button->y, 1, button->height, border_color);
    draw_rectangle(button->x, button->y + button->height - 1, button->width, 1, border_color);
    
    // Draw text (centered)
    int text_x = button->x + (button->width - strlen(button->text) * 8) / 2;
    int text_y = button->y + (button->height - 12) / 2;
    draw_text(text_x, text_y, button->text, text_color);
}

// Draw start menu
void draw_start_menu() {
    if(!start_menu.visible) return;
    
    // Draw menu background
    draw_rounded_rectangle(start_menu.x, start_menu.y, start_menu.width, start_menu.height, WIN11_SURFACE_COLOR);
    
    // Draw border
    draw_rectangle(start_menu.x, start_menu.y, start_menu.width, 1, WIN11_BORDER_COLOR);
    draw_rectangle(start_menu.x, start_menu.y, 1, start_menu.height, WIN11_BORDER_COLOR);
    draw_rectangle(start_menu.x + start_menu.width - 1, start_menu.y, 1, start_menu.height, WIN11_BORDER_COLOR);
    draw_rectangle(start_menu.x, start_menu.y + start_menu.height - 1, start_menu.width, 1, WIN11_BORDER_COLOR);
    
    // Draw title
    draw_text(start_menu.x + 10, start_menu.y + 10, "Start", WIN11_TEXT_COLOR);
    
    // Draw app buttons
    for(int i = 0; i < start_menu.app_count; i++) {
        draw_modern_button(&start_menu.apps[i]);
    }
}

// Draw context menu
void draw_context_menu() {
    if(!context_menu.visible) return;
    
    // Draw menu background
    draw_rounded_rectangle(context_menu.x, context_menu.y, context_menu.width, context_menu.height, WIN11_SURFACE_COLOR);
    
    // Draw border
    draw_rectangle(context_menu.x, context_menu.y, context_menu.width, 1, WIN11_BORDER_COLOR);
    draw_rectangle(context_menu.x, context_menu.y, 1, context_menu.height, WIN11_BORDER_COLOR);
    draw_rectangle(context_menu.x + context_menu.width - 1, context_menu.y, 1, context_menu.height, WIN11_BORDER_COLOR);
    draw_rectangle(context_menu.x, context_menu.y + context_menu.height - 1, context_menu.width, 1, WIN11_BORDER_COLOR);
    
    // Draw menu items
    for(int i = 0; i < context_menu.item_count; i++) {
        int item_y = context_menu.y + 10 + (i * 25);
        uint8_t item_color = (i == context_menu.selected_item) ? WIN11_HOVER_COLOR : WIN11_TEXT_COLOR;
        draw_text(context_menu.x + 10, item_y, context_menu.items[i], item_color);
    }
}

// Draw modern window frame with Windows 11 styling
void draw_modern_window_frame(int x, int y, int width, int height, const char* title) {
    // Draw window background
    draw_rounded_rectangle(x, y, width, height, WIN11_SURFACE_COLOR);
    
    // Draw title bar
    draw_rectangle(x, y, width, 30, WIN11_ACCENT_COLOR);
    
    // Draw title
    draw_text(x + 10, y + 8, title, WIN11_TEXT_COLOR);
    
    // Draw window controls
    int control_x = x + width - 80;
    
    // Minimize button
    draw_rounded_rectangle(control_x, y + 5, 20, 20, WIN11_SURFACE_COLOR);
    draw_text(control_x + 7, y + 8, "_", WIN11_TEXT_COLOR);
    
    // Maximize button
    control_x += 25;
    draw_rounded_rectangle(control_x, y + 5, 20, 20, WIN11_SURFACE_COLOR);
    draw_text(control_x + 7, y + 8, "[]", WIN11_TEXT_COLOR);
    
    // Close button
    control_x += 25;
    draw_rounded_rectangle(control_x, y + 5, 20, 20, WIN11_ACTIVE_COLOR);
    draw_text(control_x + 7, y + 8, "X", WIN11_TEXT_COLOR);
}

// Draw rounded rectangle (simplified - just draws a rectangle)
void draw_rounded_rectangle(int x, int y, int width, int height, uint8_t color) {
    draw_rectangle(x, y, width, height, color);
}

// Draw gradient background
void draw_gradient_background() {
    for(int y = 0; y < 480; y++) {
        uint8_t color = WIN11_BACKGROUND_COLOR + (y / 100);
        if(color > WIN11_ACCENT_COLOR) color = WIN11_ACCENT_COLOR;
        
        for(int x = 0; x < 640; x++) {
            draw_pixel(x, y, color);
        }
    }
}

// Draw modern taskbar
void draw_modern_taskbar() {
    // Draw taskbar background
    draw_rectangle(0, 440, 640, 40, WIN11_SURFACE_COLOR);
    
    // Draw top border
    draw_rectangle(0, 440, 640, 1, WIN11_BORDER_COLOR);
    
    // Draw start button
    button_t start_button = {0, 440, 60, 40, "Win", BUTTON_NORMAL, NULL};
    draw_modern_button(&start_button);
    
    // Draw taskbar buttons
    for(int i = 0; i < taskbar_button_count; i++) {
        draw_modern_button(&taskbar_buttons[i]);
    }
}

// Show context menu
void show_context_menu(int x, int y) {
    context_menu.x = x;
    context_menu.y = y;
    context_menu.visible = 1;
    context_menu.selected_item = -1;
}

// Hide context menu
void hide_context_menu() {
    context_menu.visible = 0;
}

// Handle GUI clicks
int handle_gui_click(int x, int y) {
    // Check start menu
    if(start_menu.visible) {
        if(x < start_menu.x || x > start_menu.x + start_menu.width ||
           y < start_menu.y || y > start_menu.y + start_menu.height) {
            start_menu.visible = 0;
        } else {
            // Check app buttons
            for(int i = 0; i < start_menu.app_count; i++) {
                button_t* app = &start_menu.apps[i];
                if(x >= app->x && x < app->x + app->width &&
                   y >= app->y && y < app->y + app->height) {
                    if(app->on_click) {
                        app->on_click();
                    }
                    start_menu.visible = 0;
                    return 1;
                }
            }
        }
    }
    
    // Check context menu
    if(context_menu.visible) {
        if(x < context_menu.x || x > context_menu.x + context_menu.width ||
           y < context_menu.y || y > context_menu.y + context_menu.height) {
            hide_context_menu();
        } else {
            // Check menu items
            int item_y = context_menu.y + 10;
            for(int i = 0; i < context_menu.item_count; i++) {
                if(y >= item_y && y < item_y + 20) {
                    context_menu.selected_item = i;
                    hide_context_menu();
                    return 1;
                }
                item_y += 25;
            }
        }
    }
    
    // Check start button
    if(x < 60 && y >= 440 && y < 480) {
        start_menu.visible = !start_menu.visible;
        return 1;
    }
    
    return 0;
}

// Helper functions (these would be implemented in the kernel)
void draw_pixel(int x, int y, uint8_t color) {
    // This would be implemented in the kernel
    (void)x; (void)y; (void)color;
}

void draw_rectangle(int x, int y, int width, int height, uint8_t color) {
    // This would be implemented in the kernel
    (void)x; (void)y; (void)width; (void)height; (void)color;
}

void draw_text(int x, int y, const char* text, uint8_t color) {
    // This would be implemented in the kernel
    (void)x; (void)y; (void)text; (void)color;
}