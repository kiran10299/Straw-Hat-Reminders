import math
import wave
import struct
import os
import random

SAMPLE_RATE = 44100
MAX_AMP = 32767

def save_wav(filename, samples):
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        for s in samples:
            w.writeframes(struct.pack('<h', int(max(-1.0, min(1.0, s)) * MAX_AMP * 0.8)))

os.makedirs(r"C:\Users\Admin\.gemini\antigravity\scratch\luffy_reminder\sounds", exist_ok=True)

def generate_boing():
    # Rubber stretch: pitch goes up then wobbles
    duration = 0.6
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 150 + 600 * t + 100 * math.sin(2 * math.pi * 15 * t)
        amp = math.exp(-3 * t)
        val = amp * math.sin(2 * math.pi * freq * t)
        samples.append(val)
    return samples

def generate_step():
    # Short pop
    duration = 0.1
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 150 * math.exp(-20 * t)
        amp = math.exp(-30 * t)
        val = amp * math.sin(2 * math.pi * freq * t)
        samples.append(val)
    return samples

def generate_chime():
    # C major arpeggio: C5, E5, G5, C6
    duration = 1.0
    samples = []
    notes = [523.25, 659.25, 783.99, 1046.50]
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        val = 0
        for j, note in enumerate(notes):
            start_t = j * 0.1
            if t >= start_t:
                local_t = t - start_t
                amp = math.exp(-4 * local_t)
                val += amp * math.sin(2 * math.pi * note * local_t)
        samples.append(val / len(notes))
    return samples

def generate_angry():
    # Low thud with noise
    duration = 0.5
    samples = []
    for i in range(int(SAMPLE_RATE * duration)):
        t = i / SAMPLE_RATE
        freq = 60 + 20 * math.sin(2 * math.pi * 30 * t)
        amp = math.exp(-5 * t)
        noise = random.uniform(-1, 1) * 0.3
        val = amp * (math.sin(2 * math.pi * freq * t) + noise)
        samples.append(val)
    return samples

out_dir = r"C:\Users\Admin\.gemini\antigravity\scratch\luffy_reminder\sounds"
save_wav(os.path.join(out_dir, "boing.wav"), generate_boing())
save_wav(os.path.join(out_dir, "step.wav"), generate_step())
save_wav(os.path.join(out_dir, "chime.wav"), generate_chime())
save_wav(os.path.join(out_dir, "angry.wav"), generate_angry())
print("Sound effects generated successfully.")
