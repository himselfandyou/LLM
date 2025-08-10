/* Linker script for Windows 11-inspired OS */

ENTRY(kernel_main)
OUTPUT_FORMAT(elf32-i386)
OUTPUT_ARCH(i386)

SECTIONS
{
    /* Kernel starts at 1MB */
    . = 0x100000;
    
    /* Kernel code section */
    .text : {
        *(.text)
        *(.text.*)
    }
    
    /* Read-only data section */
    .rodata : {
        *(.rodata)
        *(.rodata.*)
    }
    
    /* Read-write data section */
    .data : {
        *(.data)
        *(.data.*)
    }
    
    /* Uninitialized data section */
    .bss : {
        *(.bss)
        *(.bss.*)
        *(COMMON)
    }
    
    /* Discard other sections */
    /DISCARD/ : {
        *(.comment)
        *(.note)
        *(.eh_frame)
        *(.debug_*)
    }
}