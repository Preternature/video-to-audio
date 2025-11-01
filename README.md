# MP4 to MP3 Extractor

A simple Python GUI application to extract audio from MP4 files with precise region selection using ffmpeg.

## Features

- 🎵 Extract full audio or specific regions from MP4 files
- 🖱️ Drag and drop interface for easy file loading
- 📊 Timeline sliders for visual percentage-based region selection
- 🎚️ Adjustable audio quality (128k, 192k, 256k, 320k)
- 🖥️ Automatic video duration detection
- 📁 Auto-generates output file next to original MP4
- ⚡ Fast extraction powered by ffmpeg

## Prerequisites

- Python 3.6 or higher
- ffmpeg installed and available in your system PATH

### Installing ffmpeg

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from: https://www.gyan.dev/ffmpeg/builds/
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg  # Fedora
```

## Installation

1. Clone or download this repository
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python mp4_to_mp3_gui.py
```

### Extracting Audio

1. **Drag and drop** your MP4 file into the drop zone
2. The app will automatically detect the video duration
3. Use the **Start** and **End** sliders to select your desired region:
   - Move sliders to set the percentage of the video to extract
   - Default: 0% to 100% (entire video)
   - Time displays update in real-time showing HH:MM:SS and percentage
4. Choose audio quality (default: 192k)
5. Click **Extract Audio**
6. The MP3 will be saved next to your original MP4 with the name `{original_name}_mp3extracted.mp3`

### Usage Examples

**Extract entire audio:**
- Leave sliders at default: Start 0%, End 100%

**Extract first half of video:**
- Start: 0%
- End: 50%

**Extract middle section:**
- Start: 25%
- End: 75%

**Extract last 10%:**
- Start: 90%
- End: 100%

## Troubleshooting

**"ffmpeg not found" error:**
- Make sure ffmpeg is installed and in your system PATH
- Test by running `ffmpeg -version` in your terminal

**GUI doesn't open:**
- Ensure you have tkinter installed (usually comes with Python)
- On Linux: `sudo apt install python3-tk`

## License

MIT License - Feel free to use and modify as needed!
