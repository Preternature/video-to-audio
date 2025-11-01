#!/usr/bin/env python3
"""
MP4 to MP3 Extractor - Extract audio regions from MP4 files with a GUI
"""

import tkinter as tk
from tkinter import messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess
import os
from pathlib import Path
import threading
import re


class MP4ToMP3Extractor:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 to MP3 Extractor")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        self.input_file = ""
        self.video_duration = 0
        self.start_percent = 0
        self.end_percent = 100

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Drag and drop area
        ttk.Label(main_frame, text="Drag and Drop MP4 File Here:").grid(row=0, column=0, sticky=tk.W, pady=5)

        drop_frame = tk.Frame(main_frame, bg="#e0e0e0", relief=tk.SUNKEN, borderwidth=2)
        drop_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, ipady=30)

        self.drop_label = tk.Label(drop_frame, text="Drop MP4 file here",
                                   bg="#e0e0e0", fg="#666666",
                                   font=('TkDefaultFont', 12))
        self.drop_label.pack(expand=True, fill=tk.BOTH)

        # Enable drag and drop
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)

        # Video info display
        self.video_info_label = ttk.Label(main_frame, text="No file loaded", foreground="gray")
        self.video_info_label.grid(row=2, column=0, columnspan=2, pady=5)

        # Timeline slider frame
        timeline_frame = ttk.LabelFrame(main_frame, text="Timeline Selection", padding="10")
        timeline_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(timeline_frame, text="Start:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_scale = ttk.Scale(timeline_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    command=self.update_timeline_labels)
        self.start_scale.set(0)
        self.start_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.start_time_label = ttk.Label(timeline_frame, text="00:00:00 (0%)")
        self.start_time_label.grid(row=0, column=2, sticky=tk.W, padx=5)

        ttk.Label(timeline_frame, text="End:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_scale = ttk.Scale(timeline_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                  command=self.update_timeline_labels)
        self.end_scale.set(100)
        self.end_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.end_time_label = ttk.Label(timeline_frame, text="00:00:00 (100%)")
        self.end_time_label.grid(row=1, column=2, sticky=tk.W, padx=5)

        timeline_frame.columnconfigure(1, weight=1)

        # Audio quality
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)

        ttk.Label(quality_frame, text="Audio Quality:").pack(side=tk.LEFT, padx=(0, 5))
        self.quality_var = tk.StringVar(value="192k")
        quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var,
                                     values=["128k", "192k", "256k", "320k"],
                                     state="readonly", width=10)
        quality_combo.pack(side=tk.LEFT)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Drop a file to begin", foreground="gray")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)

        # Extract button
        self.extract_button = ttk.Button(main_frame, text="Extract Audio",
                                         command=self.extract_audio, state=tk.DISABLED)
        self.extract_button.grid(row=7, column=0, columnspan=2, pady=10)

    def on_drop(self, event):
        # Get the dropped file path
        file_path = event.data
        # Remove curly braces if present (Windows quirk)
        file_path = file_path.strip('{}')

        if not file_path.lower().endswith('.mp4'):
            messagebox.showerror("Error", "Please drop an MP4 file")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File does not exist")
            return

        self.input_file = file_path
        self.load_video_info(file_path)

    def load_video_info(self, file_path):
        # Update UI
        file_name = Path(file_path).name
        self.drop_label.config(text=f"📹 {file_name}", fg="#000000")

        # Get video duration
        duration = self.get_video_duration(file_path)
        if duration > 0:
            self.video_duration = duration
            duration_str = self.format_time(duration)
            self.video_info_label.config(text=f"Duration: {duration_str}", foreground="black")
            self.status_label.config(text="Ready to extract", foreground="green")
            self.extract_button.config(state=tk.NORMAL)
            self.update_timeline_labels()
        else:
            self.video_info_label.config(text="Could not detect video duration", foreground="red")
            self.status_label.config(text="Error loading video", foreground="red")

    def get_video_duration(self, file_path):
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                   "-of", "default=noprint_wrappers=1:nokey=1", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception:
            pass
        return 0

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def update_timeline_labels(self, *args):
        if self.video_duration == 0:
            return

        start_percent = self.start_scale.get()
        end_percent = self.end_scale.get()

        # Ensure start is before end
        if start_percent >= end_percent:
            if args:  # If called from slider movement
                # Adjust the other slider
                if self.start_scale.identify(0, 0):  # Start was moved
                    self.end_scale.set(min(start_percent + 1, 100))
                    end_percent = self.end_scale.get()
                else:  # End was moved
                    self.start_scale.set(max(end_percent - 1, 0))
                    start_percent = self.start_scale.get()

        start_time = (start_percent / 100) * self.video_duration
        end_time = (end_percent / 100) * self.video_duration

        self.start_time_label.config(text=f"{self.format_time(start_time)} ({start_percent:.0f}%)")
        self.end_time_label.config(text=f"{self.format_time(end_time)} ({end_percent:.0f}%)")

    def validate_inputs(self):
        if not self.input_file:
            messagebox.showerror("Error", "Please drop an MP4 file")
            return False

        if not os.path.exists(self.input_file):
            messagebox.showerror("Error", "Input file does not exist")
            return False

        return True

    def get_output_path(self):
        input_path = Path(self.input_file)
        output_name = f"{input_path.stem}_mp3extracted.mp3"
        return str(input_path.parent / output_name)

    def build_ffmpeg_command(self):
        output_file = self.get_output_path()
        quality = self.quality_var.get()

        start_percent = self.start_scale.get()
        end_percent = self.end_scale.get()

        start_time = (start_percent / 100) * self.video_duration
        end_time = (end_percent / 100) * self.video_duration
        duration = end_time - start_time

        cmd = ["ffmpeg", "-y"]  # -y to overwrite output file

        # Add start time if not at beginning
        if start_time > 0:
            cmd.extend(["-ss", str(start_time)])

        # Add input file
        cmd.extend(["-i", self.input_file])

        # Add duration (end time - start time)
        if duration < self.video_duration:
            cmd.extend(["-t", str(duration)])

        # Audio codec and quality settings
        cmd.extend([
            "-vn",  # No video
            "-acodec", "libmp3lame",  # MP3 codec
            "-b:a", quality,  # Audio bitrate
            output_file
        ])

        return cmd, output_file

    def run_extraction(self):
        try:
            cmd, output_file = self.build_ffmpeg_command()

            # Run ffmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self.root.after(0, lambda: self.extraction_complete(True, output_file))
            else:
                error_msg = stderr if stderr else "Unknown error"
                self.root.after(0, lambda: self.extraction_complete(False, output_file, error_msg))

        except FileNotFoundError:
            self.root.after(0, lambda: self.extraction_complete(
                False, None, "ffmpeg not found. Please install ffmpeg and add it to your PATH"
            ))
        except Exception as e:
            self.root.after(0, lambda: self.extraction_complete(False, None, str(e)))

    def extraction_complete(self, success, output_file, error_msg=None):
        self.progress.stop()
        self.extract_button.config(state=tk.NORMAL)

        if success:
            self.status_label.config(text="Extraction complete!", foreground="green")
            messagebox.showinfo("Success", f"Audio extracted successfully to:\n{output_file}")
        else:
            self.status_label.config(text="Extraction failed", foreground="red")
            messagebox.showerror("Error", f"Failed to extract audio:\n\n{error_msg}")

    def extract_audio(self):
        if not self.validate_inputs():
            return

        self.status_label.config(text="Extracting audio...", foreground="blue")
        self.extract_button.config(state=tk.DISABLED)
        self.progress.start()

        # Run extraction in a separate thread
        thread = threading.Thread(target=self.run_extraction, daemon=True)
        thread.start()


def main():
    root = TkinterDnD.Tk()
    app = MP4ToMP3Extractor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
