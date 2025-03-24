import subprocess as sp
import pygame
import os

class GifRecorder:
    def __init__(self, filename, width, height, threads=1):
        self.filename = filename
        self.width = width
        self.height = height
        self.threads = threads
        self.recording = False

        if not self.filename.endswith(".gif"):
            raise Exception("Filename must end in .gif!") 

        self.command1 = ["ffmpeg",
                "-loglevel", "verbose",
                "-y",

                "-f", "rawvideo",
                "-pix_fmt", "bgra",
                "-s", f"{self.width}x{self.height}",
                "-r", "50",
                "-i", "-",

                "-c:v", "libx264",
                "-vb", "2500k",
                "-c:a", "aac",
                "-ab", "200k",
                "-pix_fmt", "bgra", "tmp.mp4"]

        self.command2 = ["ffmpeg", "-y",
                "-threads", f"{self.threads}",
                "-i", "tmp.mp4",
                "-vf", "palettegen", 
                "palette.png"
        ]

        self.command3 = ["ffmpeg", "-y",
                "-threads", f"{self.threads}",
                "-i", "tmp.mp4",
                "-i", "palette.png",
                "-lavfi", "paletteuse",
                self.filename
        ]

        self.pipe = None

    def start_recording(self):
        if self.recording:
            raise Exception("Already recording!") 

        self.recording = True
        self.pipe = sp.Popen(self.command1, stdin=sp.PIPE)

    def upload_frame(self, surface):
        if not self.recording:
            raise Exception("Start a recording before uploading a frame!") 

        image = pygame.transform.rotate(surface, 90)
        image = pygame.surfarray.array2d(pygame.transform.flip(image, False, True))
        self.pipe.stdin.write(image)
        self.pipe.stdin.flush()

    def stop_recording(self):
        if not self.recording:
            raise Exception("You must start a recording before stopping it!") 

        self.recording = False
        self.pipe.stdin.close()
        p = sp.Popen(self.command2, stdin=sp.PIPE)
        p.wait()
        p = sp.Popen(self.command3, stdin=sp.PIPE)
        p.wait()
        os.remove("tmp.mp4")
        os.remove("palette.png")