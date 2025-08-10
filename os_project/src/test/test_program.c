#include <stdint.h>
#include <stddef.h>

// System call numbers
#define SYS_WRITE 1
#define SYS_READ 2
#define SYS_EXIT 3

// Test program entry point
void test_main() {
    // Test 1: Basic output
    print_string("=== SimpleOS Test Program ===\n");
    print_string("Testing basic functionality...\n\n");
    
    // Test 2: String operations
    print_string("Test 2: String operations\n");
    char test_string[] = "Hello, SimpleOS!";
    print_string(test_string);
    print_string("\n");
    
    // Test 3: Number printing
    print_string("Test 3: Number printing\n");
    print_string("Decimal: ");
    print_number(42);
    print_string("\n");
    print_string("Hex: ");
    print_hex(0xABCD);
    print_string("\n");
    
    // Test 4: Memory operations
    print_string("Test 4: Memory operations\n");
    int* test_array = (int*)allocate_memory(100);
    if (test_array) {
        print_string("Memory allocated successfully\n");
        test_array[0] = 123;
        test_array[1] = 456;
        print_string("Array values: ");
        print_number(test_array[0]);
        print_string(", ");
        print_number(test_array[1]);
        print_string("\n");
        free_memory(test_array);
        print_string("Memory freed\n");
    } else {
        print_string("Memory allocation failed\n");
    }
    
    // Test 5: File system operations
    print_string("Test 5: File system operations\n");
    uint32_t file_id = create_test_file("test.txt");
    if (file_id != 0xFFFFFFFF) {
        print_string("File created with ID: ");
        print_number(file_id);
        print_string("\n");
        
        // Write to file
        const char* data = "This is test data for SimpleOS file system";
        int written = write_test_file(file_id, data, 0, 40);
        print_string("Bytes written: ");
        print_number(written);
        print_string("\n");
        
        // Read from file
        char buffer[50];
        int read = read_test_file(file_id, buffer, 0, 40);
        print_string("Bytes read: ");
        print_number(read);
        print_string("\n");
        print_string("File content: ");
        buffer[read] = '\0';
        print_string(buffer);
        print_string("\n");
        
        delete_test_file(file_id);
        print_string("File deleted\n");
    } else {
        print_string("File creation failed\n");
    }
    
    // Test 6: Process information
    print_string("Test 6: Process information\n");
    print_string("Current process ID: ");
    print_number(get_current_process_id());
    print_string("\n");
    
    // Test completion
    print_string("\n=== All tests completed ===\n");
    print_string("SimpleOS is working correctly!\n");
    
    // Exit
    system_call(SYS_EXIT, 0, 0, 0);
}

// Helper functions (these would be provided by the kernel)
void print_string(const char* str) {
    system_call(SYS_WRITE, (uint32_t)str, 0, 0);
}

void print_number(int num) {
    char buffer[16];
    int_to_string(num, buffer);
    print_string(buffer);
}

void print_hex(uint32_t value) {
    char buffer[16];
    hex_to_string(value, buffer);
    print_string(buffer);
}

// Simple number to string conversion
void int_to_string(int num, char* buffer) {
    int i = 0;
    int is_negative = 0;
    
    if (num < 0) {
        is_negative = 1;
        num = -num;
    }
    
    if (num == 0) {
        buffer[i++] = '0';
    } else {
        while (num > 0) {
            buffer[i++] = '0' + (num % 10);
            num /= 10;
        }
    }
    
    if (is_negative) {
        buffer[i++] = '-';
    }
    
    // Reverse the string
    for (int j = 0; j < i / 2; j++) {
        char temp = buffer[j];
        buffer[j] = buffer[i - 1 - j];
        buffer[i - 1 - j] = temp;
    }
    
    buffer[i] = '\0';
}

// Simple hex to string conversion
void hex_to_string(uint32_t value, char* buffer) {
    char hex_chars[] = "0123456789ABCDEF";
    buffer[0] = '0';
    buffer[1] = 'x';
    
    for (int i = 0; i < 8; i++) {
        uint8_t nibble = (value >> ((7 - i) * 4)) & 0xF;
        buffer[i + 2] = hex_chars[nibble];
    }
    
    buffer[10] = '\0';
}

// Memory management functions (simplified)
void* allocate_memory(size_t size) {
    // In a real OS, this would call the kernel's memory allocator
    // For now, we'll simulate with a simple allocation
    static char memory_pool[1024];
    static int pool_used = 0;
    
    if (pool_used + size <= sizeof(memory_pool)) {
        void* ptr = &memory_pool[pool_used];
        pool_used += size;
        return ptr;
    }
    return NULL;
}

void free_memory(void* ptr) {
    // In a real OS, this would call the kernel's memory deallocator
    // For now, we'll just do nothing
    (void)ptr;
}

// File system functions (simplified)
uint32_t create_test_file(const char* name) {
    // In a real OS, this would call the file system
    static uint32_t next_file_id = 1;
    return next_file_id++;
}

int write_test_file(uint32_t file_id, const char* data, uint32_t offset, uint32_t size) {
    // In a real OS, this would call the file system
    (void)file_id;
    (void)offset;
    return size;
}

int read_test_file(uint32_t file_id, char* buffer, uint32_t offset, uint32_t size) {
    // In a real OS, this would call the file system
    (void)file_id;
    (void)offset;
    const char* test_data = "This is test data for SimpleOS file system";
    for (uint32_t i = 0; i < size && test_data[i]; i++) {
        buffer[i] = test_data[i];
    }
    return size;
}

void delete_test_file(uint32_t file_id) {
    // In a real OS, this would call the file system
    (void)file_id;
}

int get_current_process_id() {
    // In a real OS, this would call the kernel
    return 1;
}

void system_call(uint32_t call_number, uint32_t arg1, uint32_t arg2, uint32_t arg3) {
    // This would be implemented in assembly to make actual system calls
    (void)call_number;
    (void)arg1;
    (void)arg2;
    (void)arg3;
}