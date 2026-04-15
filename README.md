# Paras Project

This project records audio from the microphone and plays it back through the laptop speakers using a sequence of Aphex Twin-inspired distortion effects.

## How it works

- The script records a single audio take from the default microphone.
- It then plays that take back through 10 sequential exchanges.
- Each exchange increases the intensity of the effects gradually.
- The first exchange remains mostly clean, and later exchanges add more distortion and filtering until the final exchange is heavily processed.
- After 10 exchanges, the script waits for 15 minutes and then repeats the entire recording + playback cycle indefinitely.

## Effects applied per exchange

Each exchange may include one or more of the following:

- random dry vocal segment layering
- 12-semitone pitch shift down
- heavy distortion / bitcrush
- low-frequency ring modulation (10–80 Hz)
- low-pass filtering with resonance
- subtle reverb
- gradual intensity increase over exchanges

## Requirements

- Python 3
- `numpy`
- `sounddevice`

## Setup

1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install numpy sounddevice
   ```

## Run

```bash
python index.py
```

The script will continue looping after each complete 10-exchange cycle, waiting 15 minutes between cycles.

## Notes

- On macOS, you may need to allow microphone access when prompted.
- Stopping the script will end the infinite loop.
- The `index.py` file is the main program and contains the audio processing logic.
