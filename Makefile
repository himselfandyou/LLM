NASM ?= nasm
QEMU ?= qemu-system-i386

BUILD_DIR := build
BOOT_BIN := $(BUILD_DIR)/boot.bin
DISK_IMG := $(BUILD_DIR)/floppy.img

HEADLESS ?= 1
RUN_SECONDS ?= 4

QEMU_FLAGS_BASE := -drive format=raw,file=$(DISK_IMG) -boot a -no-reboot -no-shutdown
ifeq ($(HEADLESS),1)
QEMU_FLAGS := $(QEMU_FLAGS_BASE) -nographic -serial mon:stdio -display none
else
QEMU_FLAGS := $(QEMU_FLAGS_BASE) -vga std -serial stdio -monitor none
endif

.PHONY: all run clean dirs

all: dirs $(DISK_IMG)

$(BOOT_BIN): boot/boot.asm | dirs
	$(NASM) -f bin $< -o $@

$(DISK_IMG): $(BOOT_BIN) | dirs
	dd if=/dev/zero of=$@ bs=512 count=2880 status=none
	dd if=$(BOOT_BIN) of=$@ conv=notrunc status=none

run: $(DISK_IMG)
	@echo "(QEMU will auto-exit after $(RUN_SECONDS)s)"
	timeout $(RUN_SECONDS)s $(QEMU) $(QEMU_FLAGS) || true

clean:
	rm -rf $(BUILD_DIR)

dirs:
	mkdir -p $(BUILD_DIR)