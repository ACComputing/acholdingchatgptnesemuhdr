#!/usr/bin/env python3
# ============================================================
# ChatGPT's Emulator NES Python
# AC + ChatGPT
# (C) 1999-2026 A.C Holdings
# ============================================================

import tkinter as tk
from tkinter import filedialog
import time
import struct

# ================= CONFIG =================
W, H = 256, 240
SCALE = 2

BG = "#0b0f14"
PANEL = "#111a24"
ACCENT = "#ff3b3b"


# ============================================================
# 🧠 NES CPU (6502 SKELETON)
# ============================================================
class NESCPU:
    def __init__(self, mem):
        self.mem = mem
        self.a = 0
        self.x = 0
        self.y = 0
        self.sp = 0xFD
        self.pc = 0xC000
        self.status = 0
        self.cycles = 0

    def reset(self):
        self.__init__(self.mem)

    def step(self):
        op = self.mem[self.pc]
        self.pc = (self.pc + 1) & 0xFFFF

        if op == 0x00:
            self.pc = 0xC000
        elif op == 0xEA:
            pass
        elif op == 0xA9:
            self.a = self.mem[self.pc]
            self.pc += 1
        elif op == 0xAA:
            self.x = self.a
        elif op == 0xE8:
            self.x = (self.x + 1) & 0xFF

        self.cycles += 1


# ============================================================
# 🎮 PPU (FAKE TILE OUTPUT)
# ============================================================
class NESPPU:
    def __init__(self):
        self.fb = [0] * (W * H)

    def render(self, cpu: NESCPU):
        t = int(time.time() * 10)

        for y in range(H):
            ty = y >> 4
            for x in range(W):
                tx = x >> 4
                v = (tx ^ ty ^ cpu.a ^ cpu.x ^ t) & 3
                self.fb[x + y * W] = 1 if v == 0 else 0

        return self.fb


# ============================================================
# 🎮 CORE
# ============================================================
class NESEmulator:
    def __init__(self):
        self.mem = bytearray(0x10000)
        self.cpu = NESCPU(self.mem)
        self.ppu = NESPPU()
        self.rom_loaded = False

    def load_rom(self, data: bytes):
        if data[:4] != b"NES\x1a":
            raise ValueError("Invalid NES ROM")

        prg_size = data[4] * 16 * 1024
        prg = data[16:16 + prg_size]

        self.mem[0x8000:0x8000 + len(prg)] = prg
        self.mem[0xC000:0xC000 + len(prg)] = prg

        self.cpu.pc = 0x8000
        self.rom_loaded = True

    def reset(self):
        self.cpu.reset()

    def frame(self):
        for _ in range(3000):
            self.cpu.step()
        return self.ppu.render(self.cpu)


# ============================================================
# 🪟 UI
# ============================================================
class NESApp:
    def __init__(self, root):
        self.root = root
        self.core = NESEmulator()
        self.running = False

        # ✅ UPDATED TITLE HERE
        self.root.title("ChatGPT's NES Emulator v0.1")
        self.root.geometry("980x620")
        self.root.configure(bg=BG)

        self.canvas = tk.Canvas(
            root,
            width=W * SCALE,
            height=H * SCALE,
            bg="black",
            highlightthickness=2,
            highlightbackground=ACCENT
        )
        self.canvas.pack(padx=10, pady=10)

        bar = tk.Frame(root, bg=PANEL)
        bar.pack(fill="x")

        tk.Button(bar, text="Load NES ROM", command=self.load, bg="#2a0f0f", fg=ACCENT).pack(side="left")
        tk.Button(bar, text="Run", command=self.run, bg="#2a0f0f", fg=ACCENT).pack(side="left")
        tk.Button(bar, text="Pause", command=self.pause, bg="#2a0f0f", fg=ACCENT).pack(side="left")
        tk.Button(bar, text="Reset", command=self.reset, bg="#2a0f0f", fg=ACCENT).pack(side="left")

        self.status = tk.Label(root, text="Idle", bg=BG, fg=ACCENT)
        self.status.pack()

        self.loop()

    def load(self):
        path = filedialog.askopenfilename(filetypes=[("NES ROM", "*.nes")])
        if not path:
            return
        with open(path, "rb") as f:
            self.core.load_rom(f.read())
        self.status.config(text="NES ROM Loaded")

    def run(self):
        if self.core.rom_loaded:
            self.running = True
            self.status.config(text="Running")

    def pause(self):
        self.running = False
        self.status.config(text="Paused")

    def reset(self):
        self.core.reset()
        self.status.config(text="Reset")

    def draw(self, fb):
        self.canvas.delete("all")
        for y in range(H):
            for x in range(W):
                if fb[x + y * W]:
                    self.canvas.create_rectangle(
                        x * SCALE,
                        y * SCALE,
                        (x + 1) * SCALE,
                        (y + 1) * SCALE,
                        fill=ACCENT,
                        outline=""
                    )

    def loop(self):
        if self.running and self.core.rom_loaded:
            fb = self.core.frame()
            self.draw(fb)

        self.root.after(16, self.loop)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    NESApp(root)
    root.mainloop()
