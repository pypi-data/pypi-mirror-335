import os
import pathlib
import subprocess
import uuid

try:
    import pygame.image
    from pygame import Surface
except ModuleNotFoundError:
    pygame = object()  # type: ignore

from sneks.engine.config.instantiation import config


class Recorder:
    def __init__(self):
        self.identifier = uuid.uuid4()
        self.i = 0
        self.prefix = pathlib.Path(config.graphics.record_prefix)
        self.prefix.mkdir(exist_ok=True)
        (self.prefix / "pics").mkdir(exist_ok=True)
        (self.prefix / "movies").mkdir(exist_ok=True)

    def reset(self):
        self.identifier = uuid.uuid4()
        self.i = 0

    def record_frame(self, screen: Surface):
        pygame.image.save(
            screen,
            str(self.prefix / "pics" / f"pic_{self.identifier}_{self.i:04d}.png"),
        )
        self.i += 1

    def animate_game(self):
        import imageio_ffmpeg

        args = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-framerate",
            f"{config.graphics.record_fps}",
            "-i",
            str(self.prefix / "pics" / f"pic_{self.identifier}_%04d.png"),
            "-vcodec",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(self.prefix / "movies" / f"game_{self.identifier}.mp4"),
        ]

        subprocess.run(args)

        for image in self.prefix.glob(f"pics/pic_{self.identifier}_*.png"):
            os.remove(str(image))
