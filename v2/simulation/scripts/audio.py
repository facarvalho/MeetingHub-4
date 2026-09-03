"""
Pass a test signal through the *simulated* monitor chain transfer function
(laptop line-in  ->  J6.T headset tip, all pots max, 32 ohm load) and write:

    v2/simulation/audio_in.wav    the dry source
    v2/simulation/audio_out.wav   what the TRRS headset jack delivers

Same idea as a Proteus "Audio Out" probe, done offline: H(f) comes from the MNA
AC sweep, the signal is filtered by FFT.  audio_out keeps the true relative
level, so the ~-11 dB loaded loss and the bass roll-off are audible.
"""
import sys, os, numpy as np, wave
sys.path.insert(0, os.path.dirname(__file__))
from validate import build_chain
OUT = os.path.join(os.path.dirname(__file__), "..")
FS = 48000

# --- transfer function laptop-in -> J6.T -------------------------------
c = build_chain(nsrc=1, rv_frac=1.0, master_frac=1.0, load=32.0, src_ac=[1.0])
fg = np.concatenate([[0.0], np.logspace(-1, np.log10(FS/2), 4000)])
_, r = c.ac(fg[1:])
Hf = np.concatenate([[0.0+0j], r["j6t"]])          # gain at DC = 0 (blocked)

# --- test signal: tone steps then a log sweep -------------------------
def tone(f, dur, amp=0.30):
    t = np.arange(int(dur*FS))/FS
    env = np.minimum(np.minimum(t/0.01, 1), (dur-t)/0.01).clip(0, 1)
    return amp*np.sin(2*np.pi*f*t)*env
def sweep(f0, f1, dur, amp=0.30):
    t = np.arange(int(dur*FS))/FS
    k = (f1/f0)**(1/dur)
    ph = 2*np.pi*f0*(k**t - 1)/np.log(k)
    env = np.minimum(np.minimum(t/0.02, 1), (dur-t)/0.02).clip(0, 1)
    return amp*np.sin(ph)*env

sig = np.concatenate([
    tone(1000, 1.0), np.zeros(int(0.15*FS)),
    tone(100, 1.0),  np.zeros(int(0.15*FS)),
    tone(40, 1.0),   np.zeros(int(0.15*FS)),
    sweep(20, 20000, 4.0),
])

# --- filter by H(f) --------------------------------------------------
N = len(sig)
freqs = np.fft.rfftfreq(N, 1/FS)
H = np.interp(freqs, fg, Hf.real) + 1j*np.interp(freqs, fg, Hf.imag)
out = np.fft.irfft(np.fft.rfft(sig) * H, n=N)

def wav(path, x, gain=1.0):
    y = np.clip(x*gain, -1, 1)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(FS)
        w.writeframes((y*32767).astype("<i2").tobytes())

wav(f"{OUT}/audio_in.wav",  sig)
wav(f"{OUT}/audio_out.wav", out)                     # true relative level
wav(f"{OUT}/audio_out_normalized.wav", out, gain=0.9/np.max(np.abs(out)))
print(f"peak dry {np.max(np.abs(sig)):.3f}   peak wet {np.max(np.abs(out)):.3f}   "
      f"loaded loss {20*np.log10(np.max(np.abs(out))/np.max(np.abs(sig))):+.1f} dB")
