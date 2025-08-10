; Windows 11-inspired Bootloader
; This bootloader loads the kernel and displays a modern loading screen

[org 0x7c00]
[bits 16]

; Initialize segment registers
    mov ax, 0
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7c00

; Set video mode to 640x480 with 256 colors
    mov ax, 0x13
    int 0x10

; Display Windows 11 loading screen
    call display_loading_screen

; Load kernel from disk
    mov ah, 0x02                ; BIOS read sector function
    mov al, 50                  ; Number of sectors to read (larger kernel)
    mov ch, 0                   ; Cylinder 0
    mov cl, 2                   ; Sector 2 (sector 1 is bootloader)
    mov dh, 0                   ; Head 0
    mov dl, 0x80                ; Drive 0 (first hard disk)
    mov bx, 0x1000              ; Load kernel to 0x1000
    int 0x13                    ; BIOS interrupt

    jc disk_error               ; Jump if error (carry flag set)

; Show "Starting Windows 11" message
    call show_starting_message

; Jump to kernel
    jmp 0x1000

; Display Windows 11 loading screen
display_loading_screen:
    ; Clear screen with dark blue background
    mov ax, 0xA000
    mov es, ax
    mov di, 0
    mov cx, 640*480
    mov al, 0x01  ; Dark blue color
    rep stosb
    
    ; Draw Windows logo (simplified)
    call draw_windows_logo
    
    ; Draw loading bar
    call draw_loading_bar
    
    ; Display "Windows 11" text
    mov si, windows11_text
    mov cx, 320
    mov dx, 200
    call draw_text_centered
    
    ; Display "Loading..." text
    mov si, loading_text
    mov cx, 320
    mov dx, 250
    call draw_text_centered
    
    ret

; Draw simplified Windows logo
draw_windows_logo:
    ; Draw 4 squares representing Windows logo
    mov ax, 0xA000
    mov es, ax
    
    ; Square 1 (top-left)
    mov di, (200-20)*640 + (280-20)
    mov cx, 20
    mov dx, 20
    call draw_square
    
    ; Square 2 (top-right)
    mov di, (200-20)*640 + (320+20)
    mov cx, 20
    mov dx, 20
    call draw_square
    
    ; Square 3 (bottom-left)
    mov di, (200+20)*640 + (280-20)
    mov cx, 20
    mov dx, 20
    call draw_square
    
    ; Square 4 (bottom-right)
    mov di, (200+20)*640 + (320+20)
    mov cx, 20
    mov dx, 20
    call draw_square
    
    ret

; Draw a square
draw_square:
    push di
    mov bx, di
    mov al, 0x0F  ; White color
    
.loop_y:
    push di
    mov cx, 20
    rep stosb
    pop di
    add di, 640
    dec dx
    jnz .loop_y
    
    pop di
    ret

; Draw loading bar
draw_loading_bar:
    ; Draw background bar
    mov ax, 0xA000
    mov es, ax
    mov di, (300-5)*640 + 200
    mov cx, 240
    mov dx, 10
    mov al, 0x08  ; Dark gray
    call draw_rectangle
    
    ; Draw progress bar
    mov di, (300-5)*640 + 200
    mov cx, 0     ; Start with 0 width
    mov dx, 10
    mov al, 0x0B  ; Light blue
    call draw_rectangle
    
    ; Animate loading bar
    mov cx, 240
.animate:
    push cx
    mov di, (300-5)*640 + 200
    mov ax, 240
    sub ax, cx
    add di, ax
    mov cx, 1
    mov dx, 10
    mov al, 0x0B  ; Light blue
    call draw_rectangle
    
    ; Small delay
    mov ah, 0x86
    mov cx, 0
    mov dx, 50000
    int 0x15
    
    pop cx
    loop .animate
    
    ret

; Draw rectangle
draw_rectangle:
    push di
.loop_y:
    push di
    push cx
    rep stosb
    pop cx
    pop di
    add di, 640
    dec dx
    jnz .loop_y
    pop di
    ret

; Draw centered text
draw_text_centered:
    ; Calculate text width (simplified)
    mov si, windows11_text
    mov cx, 0
.count_loop:
    lodsb
    test al, al
    jz .draw_text
    inc cx
    jmp .count_loop
    
.draw_text:
    ; Center the text
    mov ax, 320
    sub ax, cx
    shr ax, 1
    sub ax, 3  ; Approximate character width
    
    ; Draw text
    mov si, windows11_text
    mov bx, dx
    imul bx, 640
    add bx, ax
    mov di, bx
    mov ax, 0xA000
    mov es, ax
    
.text_loop:
    lodsb
    test al, al
    jz .text_done
    mov [es:di], al
    inc di
    jmp .text_loop
    
.text_done:
    ret

; Show "Starting Windows 11" message
show_starting_message:
    ; Clear screen
    mov ax, 0x13
    int 0x10
    
    ; Draw dark background
    mov ax, 0xA000
    mov es, ax
    mov di, 0
    mov cx, 640*480
    mov al, 0x01  ; Dark blue
    rep stosb
    
    ; Display message
    mov si, starting_text
    mov cx, 320
    mov dx, 240
    call draw_text_centered
    
    ; Wait a moment
    mov ah, 0x86
    mov cx, 0
    mov dx, 100000
    int 0x15
    
    ret

; Error handling
disk_error:
    ; Clear screen
    mov ax, 0x13
    int 0x10
    
    ; Display error message
    mov si, error_msg
    mov cx, 320
    mov dx, 240
    call draw_text_centered
    
    jmp $                       ; Halt

; Data
windows11_text db 'Windows 11', 0
loading_text db 'Loading...', 0
starting_text db 'Starting Windows 11...', 0
error_msg db 'Disk read error!', 0

; Boot signature
times 510-($-$$) db 0
dw 0xaa55