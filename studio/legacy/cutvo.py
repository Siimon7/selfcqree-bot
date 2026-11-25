import sys, glob, subprocess, os, wave
import numpy as np
ep, ts, cuts = int(sys.argv[1]), sys.argv[2], [int(c) for c in sys.argv[3].split(",")]
OFF = int(sys.argv[5]) if len(sys.argv) > 5 else 0
tempo = sys.argv[4] if len(sys.argv) > 4 else "1.06"
D = "/tmp/claude-tool-results/7ba2ad0a-6e86-5b64-9d62-a58bf610f9cd"
src = glob.glob(f"{D}/mcp-Speko-blob-{ts}-*.wav")[0]
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-ar", "44100", "-ac", "1", "/tmp/full.wav"], check=True)
w = wave.open("/tmp/full.wav"); sr = w.getframerate(); x = w.readframes(w.getnframes()); w.close()
x = np.frombuffer(x, np.int16)
os.makedirs(f"vo/ep{ep:02d}", exist_ok=True)
b = [0] + [int(c * sr / 1000) for c in cuts] + [len(x)]
for k in range(len(b) - 1):
    with wave.open("/tmp/seg.wav", "wb") as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(x[b[k]:b[k + 1]].tobytes())
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", "/tmp/seg.wav", "-af",
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo=" + tempo,
        "-ar", "44100", "-ac", "1", f"vo/ep{ep:02d}/{k + OFF:02d}.wav"], check=True)
    ww = wave.open(f"vo/ep{ep:02d}/{k + OFF:02d}.wav"); print(k, round(ww.getnframes() / sr, 2), end=" | ")
