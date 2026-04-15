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

---

## Step 1 — Install Python on Mac

If you don't have Python installed yet, follow these steps:

1. Open **Terminal** (press `Command + Space`, type "Terminal", press Enter).

2. Check if Python is already installed by typing:
   ```bash
   python3 --version
   ```
   If you see something like `Python 3.x.x`, you already have it — skip to Step 2.

3. If Python is not installed, the easiest way is to install it via **Homebrew** (a package manager for Mac).

   First, install Homebrew by pasting this into Terminal:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   Follow the on-screen instructions. It may ask for your Mac password.

4. Once Homebrew is installed, install Python:
   ```bash
   brew install python
   ```

5. Verify the installation:
   ```bash
   python3 --version
   ```
   You should now see a version number.

---

## Step 2 — Download this project

Open Terminal, navigate to where you want to save the project, and clone or download it. For example, to go to your Documents folder:

```bash
cd ~/Documents
```

Then download the project (or place the project folder there manually).

Navigate into the project folder:

```bash
cd paras-project
```

---

## Step 3 — Create a virtual environment

A virtual environment is like a separate "box" for this project's Python packages — it keeps things clean and avoids conflicts with other projects.

Create the virtual environment:

```bash
python3 -m venv .venv
```

This creates a hidden folder called `.venv` inside the project.

---

## Step 4 — Activate the virtual environment

Every time you open a new Terminal window to work on this project, you need to activate the environment:

```bash
source .venv/bin/activate
```

You will know it is active because your Terminal prompt will change and show `(.venv)` at the beginning, like this:

```
(.venv) your-mac:paras-project yourname$
```

---

## Step 5 — Install dependencies

With the virtual environment active, install the required packages:

```bash
pip install numpy sounddevice
```

You only need to do this once.

---

## Step 6 — Run the project

```bash
python index.py
```

The script will record audio from your microphone, process it through 10 exchanges of effects, wait 15 minutes, and then repeat the cycle indefinitely.

> On macOS, you may need to allow microphone access when a permission popup appears — click **OK**.

To stop the script at any time, press `Control + C` in Terminal.

---

## Step 7 — Deactivate the virtual environment

When you are done working on the project and want to leave the virtual environment, simply run:

```bash
deactivate
```

Your Terminal prompt will go back to normal, and you are back to the regular system Python.

---

## Requirements

- Python 3
- `numpy`
- `sounddevice`

## Notes

- The `index.py` file is the main program and contains the audio processing logic.
- You do **not** need to reinstall packages each time — only activate the environment with `source .venv/bin/activate` and then run the script.
- Stopping the script ends the infinite loop.
