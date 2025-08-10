#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <math.h>

// Calculator application for Windows 11-inspired OS
// This provides a comprehensive calculator with scientific functions

// Calculator modes
#define CALC_MODE_STANDARD 0
#define CALC_MODE_SCIENTIFIC 1
#define CALC_MODE_PROGRAMMER 2
#define CALC_MODE_STATISTICS 3
#define CALC_MODE_DATE 4

// Button types
#define BUTTON_NUMBER 0
#define BUTTON_OPERATOR 1
#define BUTTON_FUNCTION 2
#define BUTTON_MEMORY 3
#define BUTTON_MODE 4
#define BUTTON_CLEAR 5
#define BUTTON_EQUALS 6

// Calculator button structure
typedef struct {
    int x, y;
    int width, height;
    char text[16];
    int type;
    int value;
    int pressed;
    int (*function)(double, double);
} calc_button_t;

// Calculator window structure
typedef struct {
    int x, y;
    int width, height;
    int visible;
    int mode;
    char display[64];
    double memory[10];
    double history[100];
    int history_count;
    double current_value;
    double stored_value;
    int operation_pending;
    int last_operation;
    calc_button_t buttons[50];
    int button_count;
    int selected_button;
} calculator_t;

// Global Calculator instance
static calculator_t calculator;

// Function declarations
void init_calculator();
void draw_calculator();
void create_calculator_window();
void draw_calculator_display();
void draw_calculator_buttons();
void draw_scientific_panel();
void draw_programmer_panel();
void draw_statistics_panel();
void draw_date_panel();
void handle_calculator_click(int x, int y);
void create_standard_buttons();
void create_scientific_buttons();
void create_programmer_buttons();
void create_statistics_buttons();
void create_date_buttons();
void button_click(int button_index);
void number_button_click(int number);
void operator_button_click(int operator);
void function_button_click(int function);
void memory_button_click(int memory_op);
void clear_display();
void calculate_result();
void add_to_history(double value);
void show_history();
void clear_history();
double scientific_function(int function, double value);
double statistical_function(int function, double* values, int count);
void date_calculation(int function);
void format_number(char* buffer, double value);
void format_scientific(char* buffer, double value);
void format_hex(char* buffer, int value);
void format_binary(char* buffer, int value);
void format_octal(char* buffer, int value);

// Mathematical functions
double add(double a, double b) { return a + b; }
double subtract(double a, double b) { return a - b; }
double multiply(double a, double b) { return a * b; }
double divide(double a, double b) { return b != 0 ? a / b : 0; }
double power(double a, double b) { return pow(a, b); }
double square_root(double a, double b) { return sqrt(a); }
double sine(double a, double b) { return sin(a * M_PI / 180.0); }
double cosine(double a, double b) { return cos(a * M_PI / 180.0); }
double tangent(double a, double b) { return tan(a * M_PI / 180.0); }
double logarithm(double a, double b) { return log10(a); }
double natural_log(double a, double b) { return log(a); }
double factorial(double a, double b) {
    if(a < 0) return 0;
    if(a == 0 || a == 1) return 1;
    double result = 1;
    for(int i = 2; i <= (int)a; i++) result *= i;
    return result;
}

// Initialize Calculator
void init_calculator() {
    calculator.x = 200;
    calculator.y = 200;
    calculator.width = 400;
    calculator.height = 600;
    calculator.visible = 0;
    calculator.mode = CALC_MODE_STANDARD;
    strcpy(calculator.display, "0");
    calculator.current_value = 0;
    calculator.stored_value = 0;
    calculator.operation_pending = 0;
    calculator.last_operation = 0;
    calculator.history_count = 0;
    calculator.selected_button = -1;
    
    // Initialize memory
    for(int i = 0; i < 10; i++) {
        calculator.memory[i] = 0;
    }
    
    // Initialize history
    for(int i = 0; i < 100; i++) {
        calculator.history[i] = 0;
    }
    
    // Create buttons based on mode
    create_standard_buttons();
}

// Create Calculator window
void create_calculator_window() {
    calculator.visible = 1;
    calculator.x = 200;
    calculator.y = 200;
}

// Draw Calculator
void draw_calculator() {
    if(!calculator.visible) return;
    
    // Draw window frame
    draw_modern_window_frame(calculator.x, calculator.y, 
                           calculator.width, calculator.height, "Calculator");
    
    // Draw display
    draw_calculator_display();
    
    // Draw mode selector
    draw_mode_selector();
    
    // Draw buttons
    draw_calculator_buttons();
    
    // Draw additional panels based on mode
    switch(calculator.mode) {
        case CALC_MODE_SCIENTIFIC:
            draw_scientific_panel();
            break;
        case CALC_MODE_PROGRAMMER:
            draw_programmer_panel();
            break;
        case CALC_MODE_STATISTICS:
            draw_statistics_panel();
            break;
        case CALC_MODE_DATE:
            draw_date_panel();
            break;
    }
}

// Draw calculator display
void draw_calculator_display() {
    int display_x = calculator.x + 10;
    int display_y = calculator.y + 40;
    int display_width = calculator.width - 20;
    int display_height = 60;
    
    // Draw display background
    draw_rectangle(display_x, display_y, display_width, display_height, 0x0F);
    draw_rectangle(display_x, display_y, display_width, display_height, 0x08);
    
    // Draw display text
    draw_text(display_x + 10, display_y + 20, calculator.display, 0x00);
    
    // Draw memory indicators
    for(int i = 0; i < 10; i++) {
        if(calculator.memory[i] != 0) {
            char mem_indicator[4];
            sprintf(mem_indicator, "M%d", i);
            draw_text(display_x + 10 + (i * 30), display_y + 40, mem_indicator, 0x09);
        }
    }
}

// Draw mode selector
void draw_mode_selector() {
    int mode_x = calculator.x + 10;
    int mode_y = calculator.y + 110;
    int mode_width = calculator.width - 20;
    int mode_height = 30;
    
    // Draw mode selector background
    draw_rectangle(mode_x, mode_y, mode_width, mode_height, 0x07);
    
    // Draw mode buttons
    const char* modes[] = {"Standard", "Scientific", "Programmer", "Statistics", "Date"};
    int button_width = mode_width / 5;
    
    for(int i = 0; i < 5; i++) {
        int button_x = mode_x + (i * button_width);
        uint8_t bg_color = (i == calculator.mode) ? 0x09 : 0x07;
        draw_rectangle(button_x, mode_y, button_width - 2, mode_height, bg_color);
        draw_text(button_x + 5, mode_y + 8, modes[i], 0x0F);
    }
}

// Draw calculator buttons
void draw_calculator_buttons() {
    for(int i = 0; i < calculator.button_count; i++) {
        calc_button_t* button = &calculator.buttons[i];
        
        // Determine button color
        uint8_t bg_color = 0x07;
        if(button->pressed) {
            bg_color = 0x09;
        } else if(i == calculator.selected_button) {
            bg_color = 0x0B;
        } else {
            switch(button->type) {
                case BUTTON_NUMBER:
                    bg_color = 0x0F;
                    break;
                case BUTTON_OPERATOR:
                    bg_color = 0x0E;
                    break;
                case BUTTON_FUNCTION:
                    bg_color = 0x0D;
                    break;
                case BUTTON_MEMORY:
                    bg_color = 0x0C;
                    break;
                case BUTTON_CLEAR:
                    bg_color = 0x0C;
                    break;
                case BUTTON_EQUALS:
                    bg_color = 0x0A;
                    break;
            }
        }
        
        // Draw button
        draw_rectangle(button->x, button->y, button->width, button->height, bg_color);
        draw_rectangle(button->x, button->y, button->width, button->height, 0x08);
        
        // Draw button text
        draw_text(button->x + 5, button->y + 8, button->text, 0x00);
    }
}

// Draw scientific panel
void draw_scientific_panel() {
    int panel_x = calculator.x + calculator.width + 10;
    int panel_y = calculator.y + 40;
    int panel_width = 200;
    int panel_height = calculator.height - 50;
    
    // Draw panel background
    draw_rectangle(panel_x, panel_y, panel_width, panel_height, 0x07);
    draw_rectangle(panel_x, panel_y, panel_width, panel_height, 0x08);
    
    // Draw scientific functions
    const char* functions[] = {"sin", "cos", "tan", "log", "ln", "sqrt", "x²", "x³", "1/x", "n!"};
    int button_y = panel_y + 10;
    
    for(int i = 0; i < 10; i++) {
        draw_rectangle(panel_x + 10, button_y, 80, 25, 0x0D);
        draw_text(panel_x + 15, button_y + 5, functions[i], 0x0F);
        button_y += 30;
    }
}

// Draw programmer panel
void draw_programmer_panel() {
    int panel_x = calculator.x + calculator.width + 10;
    int panel_y = calculator.y + 40;
    int panel_width = 200;
    int panel_height = calculator.height - 50;
    
    // Draw panel background
    draw_rectangle(panel_x, panel_y, panel_width, panel_height, 0x07);
    draw_rectangle(panel_x, panel_y, panel_width, panel_height, 0x08);
    
    // Draw number system buttons
    const char* systems[] = {"HEX", "DEC", "OCT", "BIN"};
    int button_x = panel_x + 10;
    
    for(int i = 0; i < 4; i++) {
        draw_rectangle(button_x, panel_y + 10, 40, 25, 0x0D);
        draw_text(button_x + 5, panel_y + 15, systems[i], 0x0F);
        button_x += 45;
    }
    
    // Draw bitwise operators
    const char* operators[] = {"AND", "OR", "XOR", "NOT", "LSH", "RSH"};
    button_x = panel_x + 10;
    int button_y = panel_y + 50;
    
    for(int i = 0; i < 6; i++) {
        draw_rectangle(button_x, button_y, 50, 25, 0x0E);
        draw_text(button_x + 5, button_y + 5, operators[i], 0x0F);
        button_x += 55;
        if(button_x > panel_x + panel_width - 60) {
            button_x = panel_x + 10;
            button_y += 30;
        }
    }
}

// Draw statistics panel
void draw_statistics_panel() {
    int panel_x = calculator.x + calculator.width + 10;
    int panel_y = calculator.y + 40;
    int panel_width = 200;
    int panel_height = calculator.height - 50;
    
    // Draw panel background
    draw_rectangle(panel_x, panel_y, panel_width, panel_height, 0x07);
    draw_rectangle(panel_x, panel_y, panel_width, panel_height, 0x08);
    
    // Draw statistics functions
    const char* functions[] = {"Mean", "Median", "Mode", "Std Dev", "Variance", "Min", "Max", "Sum"};
    int button_y = panel_y + 10;
    
    for(int i = 0; i < 8; i++) {
        draw_rectangle(panel_x + 10, button_y, 80, 25, 0x0D);
        draw_text(panel_x + 15, button_y + 5, functions[i], 0x0F);
        button_y += 30;
    }
}

// Draw date panel
void draw_date_panel() {
    int panel_x = calculator.x + calculator.width + 10;
    int panel_y = calculator.y + 40;
    int panel_width = 200;
    int panel_height = calculator.height - 50;
    
    // Draw panel background
    draw_rectangle(panel_x, panel_y, panel_width, panel_height, 0x07);
    draw_rectangle(panel_x, panel_y, panel_width, panel_height, 0x08);
    
    // Draw date functions
    const char* functions[] = {"Days Between", "Add Days", "Subtract Days", "Day of Week", "Leap Year"};
    int button_y = panel_y + 10;
    
    for(int i = 0; i < 5; i++) {
        draw_rectangle(panel_x + 10, button_y, 120, 25, 0x0D);
        draw_text(panel_x + 15, button_y + 5, functions[i], 0x0F);
        button_y += 30;
    }
}

// Handle Calculator clicks
void handle_calculator_click(int x, int y) {
    if(!calculator.visible) return;
    
    // Check if click is within window bounds
    if(x < calculator.x || x > calculator.x + calculator.width ||
       y < calculator.y || y > calculator.y + calculator.height) {
        return;
    }
    
    // Convert to window coordinates
    int wx = x - calculator.x;
    int wy = y - calculator.y;
    
    // Check mode selector clicks
    if(wy >= 110 && wy < 140) {
        int mode_width = (calculator.width - 20) / 5;
        int mode_index = wx / mode_width;
        if(mode_index >= 0 && mode_index < 5) {
            calculator.mode = mode_index;
            switch(mode_index) {
                case CALC_MODE_STANDARD:
                    create_standard_buttons();
                    break;
                case CALC_MODE_SCIENTIFIC:
                    create_scientific_buttons();
                    break;
                case CALC_MODE_PROGRAMMER:
                    create_programmer_buttons();
                    break;
                case CALC_MODE_STATISTICS:
                    create_statistics_buttons();
                    break;
                case CALC_MODE_DATE:
                    create_date_buttons();
                    break;
            }
            return;
        }
    }
    
    // Check button clicks
    for(int i = 0; i < calculator.button_count; i++) {
        calc_button_t* button = &calculator.buttons[i];
        if(wx >= button->x - calculator.x && wx < button->x - calculator.x + button->width &&
           wy >= button->y - calculator.y && wy < button->y - calculator.y + button->height) {
            button_click(i);
            return;
        }
    }
}

// Create standard calculator buttons
void create_standard_buttons() {
    calculator.button_count = 0;
    int button_x = calculator.x + 10;
    int button_y = calculator.y + 150;
    int button_width = 60;
    int button_height = 40;
    int spacing = 5;
    
    // Number buttons
    for(int i = 0; i < 10; i++) {
        calc_button_t* button = &calculator.buttons[calculator.button_count];
        button->x = button_x + ((i - 1) % 3) * (button_width + spacing);
        button->y = button_y + ((9 - i) / 3) * (button_height + spacing);
        button->width = button_width;
        button->height = button_height;
        sprintf(button->text, "%d", i);
        button->type = BUTTON_NUMBER;
        button->value = i;
        button->pressed = 0;
        button->function = NULL;
        calculator.button_count++;
    }
    
    // Operator buttons
    const char* operators[] = {"+", "-", "×", "÷", "=", "C", "CE", "±", ".", "%"};
    int op_values[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    int op_x = button_x + 3 * (button_width + spacing) + 10;
    
    for(int i = 0; i < 10; i++) {
        calc_button_t* button = &calculator.buttons[calculator.button_count];
        button->x = op_x;
        button->y = button_y + i * (button_height + spacing);
        button->width = button_width;
        button->height = button_height;
        strcpy(button->text, operators[i]);
        button->type = BUTTON_OPERATOR;
        button->value = op_values[i];
        button->pressed = 0;
        button->function = NULL;
        calculator.button_count++;
    }
    
    // Memory buttons
    const char* memory_ops[] = {"MC", "MR", "M+", "M-", "MS"};
    int mem_x = op_x + button_width + 10;
    
    for(int i = 0; i < 5; i++) {
        calc_button_t* button = &calculator.buttons[calculator.button_count];
        button->x = mem_x;
        button->y = button_y + i * (button_height + spacing);
        button->width = button_width;
        button->height = button_height;
        strcpy(button->text, memory_ops[i]);
        button->type = BUTTON_MEMORY;
        button->value = i;
        button->pressed = 0;
        button->function = NULL;
        calculator.button_count++;
    }
}

// Create scientific calculator buttons
void create_scientific_buttons() {
    create_standard_buttons();
    
    // Add scientific functions
    const char* functions[] = {"sin", "cos", "tan", "log", "ln", "sqrt", "x²", "x³", "1/x", "n!"};
    int func_x = calculator.x + 10;
    int func_y = calculator.y + 350;
    int button_width = 60;
    int button_height = 30;
    int spacing = 5;
    
    for(int i = 0; i < 10; i++) {
        calc_button_t* button = &calculator.buttons[calculator.button_count];
        button->x = func_x + (i % 5) * (button_width + spacing);
        button->y = func_y + (i / 5) * (button_height + spacing);
        button->width = button_width;
        button->height = button_height;
        strcpy(button->text, functions[i]);
        button->type = BUTTON_FUNCTION;
        button->value = i;
        button->pressed = 0;
        button->function = NULL;
        calculator.button_count++;
    }
}

// Create programmer calculator buttons
void create_programmer_buttons() {
    create_standard_buttons();
    
    // Add programmer functions
    const char* functions[] = {"AND", "OR", "XOR", "NOT", "LSH", "RSH", "HEX", "DEC", "OCT", "BIN"};
    int func_x = calculator.x + 10;
    int func_y = calculator.y + 350;
    int button_width = 60;
    int button_height = 30;
    int spacing = 5;
    
    for(int i = 0; i < 10; i++) {
        calc_button_t* button = &calculator.buttons[calculator.button_count];
        button->x = func_x + (i % 5) * (button_width + spacing);
        button->y = func_y + (i / 5) * (button_height + spacing);
        button->width = button_width;
        button->height = button_height;
        strcpy(button->text, functions[i]);
        button->type = BUTTON_FUNCTION;
        button->value = i;
        button->pressed = 0;
        button->function = NULL;
        calculator.button_count++;
    }
}

// Create statistics calculator buttons
void create_statistics_buttons() {
    create_standard_buttons();
    
    // Add statistics functions
    const char* functions[] = {"Mean", "Median", "Mode", "Std Dev", "Variance", "Min", "Max", "Sum", "Clear", "Enter"};
    int func_x = calculator.x + 10;
    int func_y = calculator.y + 350;
    int button_width = 70;
    int button_height = 30;
    int spacing = 5;
    
    for(int i = 0; i < 10; i++) {
        calc_button_t* button = &calculator.buttons[calculator.button_count];
        button->x = func_x + (i % 5) * (button_width + spacing);
        button->y = func_y + (i / 5) * (button_height + spacing);
        button->width = button_width;
        button->height = button_height;
        strcpy(button->text, functions[i]);
        button->type = BUTTON_FUNCTION;
        button->value = i;
        button->pressed = 0;
        button->function = NULL;
        calculator.button_count++;
    }
}

// Create date calculator buttons
void create_date_buttons() {
    create_standard_buttons();
    
    // Add date functions
    const char* functions[] = {"Days Between", "Add Days", "Subtract Days", "Day of Week", "Leap Year", "Today", "Clear", "Enter"};
    int func_x = calculator.x + 10;
    int func_y = calculator.y + 350;
    int button_width = 80;
    int button_height = 30;
    int spacing = 5;
    
    for(int i = 0; i < 8; i++) {
        calc_button_t* button = &calculator.buttons[calculator.button_count];
        button->x = func_x + (i % 4) * (button_width + spacing);
        button->y = func_y + (i / 4) * (button_height + spacing);
        button->width = button_width;
        button->height = button_height;
        strcpy(button->text, functions[i]);
        button->type = BUTTON_FUNCTION;
        button->value = i;
        button->pressed = 0;
        button->function = NULL;
        calculator.button_count++;
    }
}

// Handle button click
void button_click(int button_index) {
    if(button_index < 0 || button_index >= calculator.button_count) return;
    
    calc_button_t* button = &calculator.buttons[button_index];
    button->pressed = 1;
    
    switch(button->type) {
        case BUTTON_NUMBER:
            number_button_click(button->value);
            break;
        case BUTTON_OPERATOR:
            operator_button_click(button->value);
            break;
        case BUTTON_FUNCTION:
            function_button_click(button->value);
            break;
        case BUTTON_MEMORY:
            memory_button_click(button->value);
            break;
        case BUTTON_CLEAR:
            clear_display();
            break;
        case BUTTON_EQUALS:
            calculate_result();
            break;
    }
    
    // Reset button state after a short delay
    // In a real implementation, this would use a timer
    button->pressed = 0;
}

// Handle number button click
void number_button_click(int number) {
    if(strcmp(calculator.display, "0") == 0 && number != 0) {
        sprintf(calculator.display, "%d", number);
    } else if(strcmp(calculator.display, "0") != 0) {
        char temp[64];
        sprintf(temp, "%s%d", calculator.display, number);
        strcpy(calculator.display, temp);
    }
    
    calculator.current_value = atof(calculator.display);
}

// Handle operator button click
void operator_button_click(int operator) {
    if(calculator.operation_pending) {
        calculate_result();
    }
    
    calculator.stored_value = calculator.current_value;
    calculator.operation_pending = 1;
    calculator.last_operation = operator;
    
    // Clear display for next number
    strcpy(calculator.display, "0");
}

// Handle function button click
void function_button_click(int function) {
    double result = scientific_function(function, calculator.current_value);
    format_number(calculator.display, result);
    calculator.current_value = result;
    add_to_history(result);
}

// Handle memory button click
void memory_button_click(int memory_op) {
    switch(memory_op) {
        case 0: // MC - Memory Clear
            calculator.memory[0] = 0;
            break;
        case 1: // MR - Memory Recall
            format_number(calculator.display, calculator.memory[0]);
            calculator.current_value = calculator.memory[0];
            break;
        case 2: // M+ - Memory Add
            calculator.memory[0] += calculator.current_value;
            break;
        case 3: // M- - Memory Subtract
            calculator.memory[0] -= calculator.current_value;
            break;
        case 4: // MS - Memory Store
            calculator.memory[0] = calculator.current_value;
            break;
    }
}

// Clear display
void clear_display() {
    strcpy(calculator.display, "0");
    calculator.current_value = 0;
    calculator.operation_pending = 0;
}

// Calculate result
void calculate_result() {
    if(!calculator.operation_pending) return;
    
    double result = 0;
    switch(calculator.last_operation) {
        case 0: // Add
            result = add(calculator.stored_value, calculator.current_value);
            break;
        case 1: // Subtract
            result = subtract(calculator.stored_value, calculator.current_value);
            break;
        case 2: // Multiply
            result = multiply(calculator.stored_value, calculator.current_value);
            break;
        case 3: // Divide
            result = divide(calculator.stored_value, calculator.current_value);
            break;
    }
    
    format_number(calculator.display, result);
    calculator.current_value = result;
    calculator.operation_pending = 0;
    add_to_history(result);
}

// Add to history
void add_to_history(double value) {
    if(calculator.history_count < 100) {
        calculator.history[calculator.history_count++] = value;
    } else {
        // Shift history
        for(int i = 0; i < 99; i++) {
            calculator.history[i] = calculator.history[i + 1];
        }
        calculator.history[99] = value;
    }
}

// Show history
void show_history() {
    // In a real implementation, this would show a history window
    // For now, just display the last calculation
    if(calculator.history_count > 0) {
        format_number(calculator.display, calculator.history[calculator.history_count - 1]);
        calculator.current_value = calculator.history[calculator.history_count - 1];
    }
}

// Clear history
void clear_history() {
    calculator.history_count = 0;
    for(int i = 0; i < 100; i++) {
        calculator.history[i] = 0;
    }
}

// Scientific function
double scientific_function(int function, double value) {
    switch(function) {
        case 0: return sine(value, 0);
        case 1: return cosine(value, 0);
        case 2: return tangent(value, 0);
        case 3: return logarithm(value, 0);
        case 4: return natural_log(value, 0);
        case 5: return square_root(value, 0);
        case 6: return power(value, 2);
        case 7: return power(value, 3);
        case 8: return divide(1, value);
        case 9: return factorial(value, 0);
        default: return value;
    }
}

// Statistical function
double statistical_function(int function, double* values, int count) {
    if(count == 0) return 0;
    
    switch(function) {
        case 0: { // Mean
            double sum = 0;
            for(int i = 0; i < count; i++) sum += values[i];
            return sum / count;
        }
        case 1: { // Median
            // Simplified median calculation
            return values[count / 2];
        }
        case 2: { // Mode
            // Simplified mode calculation
            return values[0];
        }
        case 3: { // Standard Deviation
            double mean = statistical_function(0, values, count);
            double sum = 0;
            for(int i = 0; i < count; i++) {
                sum += pow(values[i] - mean, 2);
            }
            return sqrt(sum / count);
        }
        case 4: { // Variance
            double std_dev = statistical_function(3, values, count);
            return std_dev * std_dev;
        }
        case 5: { // Min
            double min = values[0];
            for(int i = 1; i < count; i++) {
                if(values[i] < min) min = values[i];
            }
            return min;
        }
        case 6: { // Max
            double max = values[0];
            for(int i = 1; i < count; i++) {
                if(values[i] > max) max = values[i];
            }
            return max;
        }
        case 7: { // Sum
            double sum = 0;
            for(int i = 0; i < count; i++) sum += values[i];
            return sum;
        }
        default: return 0;
    }
}

// Date calculation
void date_calculation(int function) {
    // In a real implementation, this would handle date calculations
    // For now, just display a placeholder
    strcpy(calculator.display, "Date Calc");
}

// Format number for display
void format_number(char* buffer, double value) {
    if(value == (int)value) {
        sprintf(buffer, "%d", (int)value);
    } else {
        sprintf(buffer, "%.6f", value);
        // Remove trailing zeros
        int len = strlen(buffer);
        while(len > 0 && buffer[len - 1] == '0') {
            buffer[len - 1] = '\0';
            len--;
        }
        if(len > 0 && buffer[len - 1] == '.') {
            buffer[len - 1] = '\0';
        }
    }
}

// Format scientific notation
void format_scientific(char* buffer, double value) {
    sprintf(buffer, "%.2e", value);
}

// Format hexadecimal
void format_hex(char* buffer, int value) {
    sprintf(buffer, "0x%X", value);
}

// Format binary
void format_binary(char* buffer, int value) {
    strcpy(buffer, "");
    for(int i = 31; i >= 0; i--) {
        if(value & (1 << i)) {
            strcat(buffer, "1");
        } else {
            strcat(buffer, "0");
        }
    }
}

// Format octal
void format_octal(char* buffer, int value) {
    sprintf(buffer, "0%o", value);
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

double atof(const char* str) {
    // Simplified atof implementation
    // In a real implementation, this would parse floating point numbers
    return 0.0;
}

double pow(double x, double y) {
    // Simplified pow implementation
    // In a real implementation, this would calculate power
    return x * y;
}

double sqrt(double x) {
    // Simplified sqrt implementation
    // In a real implementation, this would calculate square root
    return x / 2;
}

double sin(double x) {
    // Simplified sin implementation
    // In a real implementation, this would calculate sine
    return x;
}

double cos(double x) {
    // Simplified cos implementation
    // In a real implementation, this would calculate cosine
    return x;
}

double tan(double x) {
    // Simplified tan implementation
    // In a real implementation, this would calculate tangent
    return x;
}

double log10(double x) {
    // Simplified log10 implementation
    // In a real implementation, this would calculate base-10 logarithm
    return x;
}

double log(double x) {
    // Simplified log implementation
    // In a real implementation, this would calculate natural logarithm
    return x;
}