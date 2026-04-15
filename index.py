#!/usr/bin/env python3
"""Record microphone audio and play it back in 10 left/right exchanges with Aphex Twin-inspired vocal distortion."""

import argparse
import random
import sys
import time

try:
    import numpy as np
    import sounddevice as sd
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: install with `pip install numpy sounddevice`"
    ) from exc


def parse_args():
    parser = argparse.ArgumentParser(
        description="Record from microphone and play 10 exchanges with Aphex Twin-inspired distortion, then loop after a 15 minute wait."
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=5.0,
        help="Number of seconds to record from the microphone (default: 5)",
    )
    parser.add_argument(
        "-r",
        "--samplerate",
        type=int,
        default=44100,
        help="Sample rate to use for recording and playback (default: 44100)",
    )
    return parser.parse_args()


def apply_eq(signal: np.ndarray, samplerate: int, low_gain: float, mid_gain: float, high_gain: float) -> np.ndarray:
    """Apply simple low/mid/high gain shaping in the frequency domain."""
    length = len(signal)
    spectrum = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(length, d=1.0 / samplerate)

    low_mask = freqs <= 400
    mid_mask = (freqs > 400) & (freqs <= 3000)
    high_mask = freqs > 3000

    spectrum[low_mask] *= low_gain
    spectrum[mid_mask] *= mid_gain
    spectrum[high_mask] *= high_gain

    filtered = np.fft.irfft(spectrum, n=length)
    return np.clip(filtered, -1.0, 1.0)


def pitch_shift(signal: np.ndarray, semitones: float) -> np.ndarray:
    """Approximate pitch shift by resampling down then back to original length."""
    factor = 2.0 ** (-semitones / 12.0)
    if factor == 1.0:
        return signal

    original = np.arange(len(signal))
    slowed = np.interp(
        np.linspace(0, len(signal) - 1, max(2, int(len(signal) * factor))),
        original,
        signal,
    ).astype(np.float32)
    return np.interp(
        np.linspace(0, len(slowed) - 1, len(signal)),
        np.arange(len(slowed)),
        slowed,
    ).astype(np.float32)


def apply_distortion(signal: np.ndarray, amount: float) -> np.ndarray:
    """Apply a mix of fuzz and bit-crush distortion."""
    drive = 1.0 + amount * 12.0
    fuzzed = np.tanh(signal * drive)
    if amount > 0.5:
        levels = 2 ** (8 + int(8 * (amount - 0.5) / 0.5))
        fuzzed = np.round(fuzzed * levels) / float(levels)
    return np.clip((1.0 - amount) * signal + amount * fuzzed, -1.0, 1.0)


def ring_mod(signal: np.ndarray, samplerate: int, freq: float, amount: float) -> np.ndarray:
    """Apply a low-frequency ring modulator."""
    t = np.arange(len(signal)) / float(samplerate)
    carrier = np.sin(2.0 * np.pi * freq * t)
    return np.clip(signal * ((1.0 - amount) + amount * carrier), -1.0, 1.0)


def lowpass_resonant(signal: np.ndarray, samplerate: int, cutoff: float, resonance: float) -> np.ndarray:
    """Apply a simple resonant low-pass response in the frequency domain."""
    length = len(signal)
    spectrum = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(length, d=1.0 / samplerate)
    response = 1.0 / (1.0 + (freqs / cutoff) ** 4)
    response += resonance * np.exp(-((freqs - cutoff) / (cutoff * 0.2)) ** 2) * 0.25
    filtered = np.fft.irfft(spectrum * response, n=length)
    return np.clip(filtered, -1.0, 1.0)


def reverb(signal: np.ndarray, samplerate: int, wet: float) -> np.ndarray:
    """Add a short plate-style reverb tail."""
    ir_len = int(0.14 * samplerate)
    if ir_len < 1:
        return signal
    ir = np.zeros(ir_len, dtype="float32")
    taps = [0, int(0.03 * samplerate), int(0.05 * samplerate), int(0.08 * samplerate)]
    for idx, tap in enumerate(taps):
        if tap < ir_len:
            ir[tap] += 0.5 * (0.4 ** idx)
    reverbed = np.convolve(signal, ir, mode="full")[: len(signal)]
    return np.clip((1.0 - wet) * signal + wet * reverbed, -1.0, 1.0)


def select_random_vocal_segment(signal: np.ndarray, samplerate: int, duration: float = 0.8) -> np.ndarray:
    """Select a random dry vocal segment from the recorded signal."""
    segment_len = min(len(signal), int(duration * samplerate))
    if segment_len <= 0:
        return signal.copy()
    start = random.randrange(0, len(signal) - segment_len + 1)
    return signal[start : start + segment_len].copy()


def overlay_segment(base: np.ndarray, segment: np.ndarray, amount: float) -> np.ndarray:
    """Overlay a processed vocal segment at a random position."""
    output = base.copy()
    if len(segment) >= len(base):
        output += segment[: len(base)] * amount
    else:
        start = random.randrange(0, len(base) - len(segment) + 1)
        output[start : start + len(segment)] += segment * amount
    return np.clip(output, -1.0, 1.0)


def apply_aphex_vocal_layer(signal: np.ndarray, samplerate: int, intensity: float) -> np.ndarray:
    """Add a processed dry vocal layer inspired by Aphex Twin vocals."""
    segment = select_random_vocal_segment(signal, samplerate)
    segment = pitch_shift(segment, 12.0)
    segment = apply_distortion(segment, min(1.0, 0.25 + intensity * 0.75))
    segment = ring_mod(segment, samplerate, freq=10.0 + 70.0 * random.random(), amount=min(1.0, 0.25 + intensity * 0.5))
    segment = lowpass_resonant(segment, samplerate, cutoff=1600.0, resonance=0.4 + 0.4 * intensity)
    segment = reverb(segment, samplerate, wet=0.12 + 0.16 * intensity)
    return overlay_segment(signal, segment, amount=0.16 + 0.24 * intensity)


def choose_cycle_effects() -> dict:
    """Choose a random set of distortion effects to apply for a cycle."""
    effects = [
        "vocal_layer",
        "distortion",
        "ring_mod",
        "lowpass",
        "reverb",
    ]
    chosen = set(random.sample(effects, k=random.randint(3, len(effects))))
    return {
        "vocal_layer": "vocal_layer" in chosen,
        "distortion": "distortion" in chosen,
        "ring_mod": "ring_mod" in chosen,
        "lowpass": "lowpass" in chosen,
        "reverb": "reverb" in chosen,
    }


def main() -> int:
    args = parse_args()
    duration = args.duration
    samplerate = args.samplerate

    if duration <= 0:
        print("Duration must be greater than zero.", file=sys.stderr)
        return 1

    print(
        f"Recording {duration:.1f}s from the microphone and playing back 10 Aphex Twin-style distorted exchanges per cycle..."
    )
    print("Press Ctrl+C to cancel during recording or playback.")

    try:
        cycle = 0
        while True:
            cycle += 1
            print(f"\n=== Cycle {cycle}: recording and playback begin ===")

            recording = sd.rec(
                int(duration * samplerate),
                samplerate=samplerate,
                channels=1,
                dtype="float32",
            )
            sd.wait()

            mono = recording[:, 0]
            cycle_effects = choose_cycle_effects()
            print(f"Cycle {cycle} effect set: {', '.join(k for k, v in cycle_effects.items() if v)}")
            for i in range(10):
                intensity = i * 0.1
                volume = (i + 1) / 10.0
                low_gain = 1.0 + 0.1 * (i + 1)
                mid_gain = max(0.0, 1.0 - 0.1 * (i + 1))
                high_gain = max(0.0, 1.0 - 0.1 * (i + 1))

                processed = apply_eq(mono * volume, samplerate, low_gain, mid_gain, high_gain)
                if intensity > 0.0:
                    if cycle_effects["distortion"]:
                        processed = apply_distortion(processed, min(1.0, 0.18 + intensity * 0.6))
                    if cycle_effects["ring_mod"]:
                        processed = ring_mod(
                            processed,
                            samplerate,
                            freq=10.0 + 70.0 * random.random(),
                            amount=min(1.0, 0.15 + intensity * 0.5),
                        )
                    if cycle_effects["lowpass"]:
                        processed = lowpass_resonant(
                            processed,
                            samplerate,
                            cutoff=1600.0 - intensity * 800.0,
                            resonance=0.35 + intensity * 0.45,
                        )
                    if cycle_effects["reverb"]:
                        processed = reverb(processed, samplerate, wet=0.1 + intensity * 0.22)
                    if cycle_effects["vocal_layer"]:
                        processed = apply_aphex_vocal_layer(processed, samplerate, intensity * 0.85)

                stereo_left = np.zeros((processed.shape[0], 2), dtype="float32")
                stereo_left[:, 0] = processed
                stereo_right = np.zeros((processed.shape[0], 2), dtype="float32")
                stereo_right[:, 1] = processed

                print(
                    f"Exchange {i + 1}/10: volume {volume * 100:.0f}%, "
                    f"effect intensity {intensity * 100:.0f}%, "
                    f"low x{low_gain:.1f}, mid x{mid_gain:.1f}, high x{high_gain:.1f}"
                )

                sd.play(stereo_left, samplerate=samplerate)
                sd.wait()
                print("Played on left speaker.")

                sd.play(stereo_right, samplerate=samplerate)
                sd.wait()
                print("Played on right speaker.")

            print("Cycle complete. Waiting 15 minutes before the next cycle...")
            time.sleep(15 * 60)

    except KeyboardInterrupt:
        print("Interrupted by user.")
        return 0
    except Exception as exc:
        print(f"Audio error: {exc}", file=sys.stderr)
        return 1

    print("Playback finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
