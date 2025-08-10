; Simple boot sector that prints a message in 16-bit real mode
; Prints to both VGA (int 0x10) and COM1 serial so it works headless with -serial stdio
; Assemble: nasm -f bin boot.asm -o boot.bin

BITS 16
ORG 0x7C00

%define COM1 0x3F8

start:
  cli
  xor ax, ax
  mov ds, ax
  mov es, ax
  mov ss, ax
  mov sp, 0x7C00
  sti

  ; init serial COM1: 115200 8N1
  call init_serial

  mov si, message
.print_char:
  lodsb
  test al, al
  jz .done
  ; teletype to screen
  mov ah, 0x0E
  mov bh, 0x00
  mov bl, 0x07
  int 0x10
  ; also write to serial
  push ax
  mov al, [si-1]
  call serial_write
  pop ax
  jmp .print_char
.done:
  jmp $

; Initialize COM1 serial port to 115200 8N1
init_serial:
  mov dx, COM1 + 1    ; Interrupt Enable Register
  mov al, 0x00
  out dx, al
  mov dx, COM1 + 3    ; Line Control Register
  mov al, 0x80        ; Enable DLAB
  out dx, al
  mov dx, COM1 + 0    ; Divisor Latch Low (115200 baud => divisor 1)
  mov al, 0x01
  out dx, al
  mov dx, COM1 + 1    ; Divisor Latch High
  xor al, al
  out dx, al
  mov dx, COM1 + 3    ; Line Control Register
  mov al, 0x03        ; 8 bits, no parity, one stop bit
  out dx, al
  mov dx, COM1 + 2    ; FIFO Control Register
  mov al, 0xC7        ; Enable FIFO, clear, 14-byte threshold
  out dx, al
  mov dx, COM1 + 4    ; Modem Control Register
  mov al, 0x0B        ; IRQs enabled, RTS/DSR set
  out dx, al
  ret

; Write AL to serial COM1, waiting for transmitter holding register empty
serial_write:
  push dx
.wait:
  mov dx, COM1 + 5    ; Line Status Register
  in al, dx
  test al, 0x20       ; THR empty?
  jz .wait
  mov dx, COM1 + 0    ; Transmit Holding Register
  pop dx
  out dx, al
  ret

message: db "Hello from your tiny OS!\r\n", 0

; Pad to 510 bytes and write boot signature 0x55AA
TIMES 510-($-$$) db 0
DW 0xAA55