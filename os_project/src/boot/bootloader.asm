; Simple x86 Bootloader
; This bootloader loads the kernel from disk and jumps to it

[org 0x7c00]                    ; BIOS loads bootloader at 0x7c00
[bits 16]                       ; Start in 16-bit real mode

; Initialize segment registers
    mov ax, 0
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7c00

; Print welcome message
    mov si, welcome_msg
    call print_string

; Load kernel from disk
    mov ah, 0x02                ; BIOS read sector function
    mov al, 15                  ; Number of sectors to read (kernel size)
    mov ch, 0                   ; Cylinder 0
    mov cl, 2                   ; Sector 2 (sector 1 is bootloader)
    mov dh, 0                   ; Head 0
    mov dl, 0x80                ; Drive 0 (first hard disk)
    mov bx, 0x1000              ; Load kernel to 0x1000
    int 0x13                    ; BIOS interrupt

    jc disk_error               ; Jump if error (carry flag set)

; Jump to kernel
    jmp 0x1000

; Print string function
print_string:
    lodsb                       ; Load next character
    or al, al                   ; Check if character is null
    jz print_done               ; If null, we're done
    mov ah, 0x0e                ; BIOS teletype function
    int 0x10                    ; BIOS interrupt
    jmp print_string
print_done:
    ret

; Error handling
disk_error:
    mov si, disk_error_msg
    call print_string
    jmp $                       ; Halt

; Data
welcome_msg db 'SimpleOS Bootloader Starting...', 0x0d, 0x0a, 0
disk_error_msg db 'Disk read error!', 0x0d, 0x0a, 0

; Boot signature
times 510-($-$$) db 0
dw 0xaa55