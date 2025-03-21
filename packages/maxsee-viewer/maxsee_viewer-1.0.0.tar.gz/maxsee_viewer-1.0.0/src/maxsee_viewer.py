# Copyright (c) 2025 Johannes Löhnert <loehnert.kde@gmx.de>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from io import BytesIO
import logging
from pathlib import Path
from queue import Queue
import tkinter as tk
import itertools as it

from ascii_designer import AutoFrame, set_toolkit
from PIL import ImageTk, Image, ImageOps

from maxsee import receive_maxsee


def L():
    return logging.getLogger(__name__)


class MaxSee(AutoFrame):
    f_menu = [
        "Quit",
        "Save",
    ]

    f_body = """
        | -
        Iframe: .
    """

    def __init__(self, receiver: Queue, interval_s=0.1):
        super().__init__()
        self.receiver: Queue = receiver
        self.interval_s = interval_s
        self.last_image = None

    def f_on_build(self):
        self[""].geometry("800x600")
        self[""].after(int(self.interval_s * 1000), self.update_jpg_loop)

    def update_jpg_loop(self):
        self[""].after(int(self.interval_s * 1000), self.update_jpg_loop)
        buf = b""
        while not self.receiver.empty():
            buf = self.receiver.get()
        if not buf:
            return
        frame: tk.Label = self["frame"]
        w, h = frame.winfo_width(), frame.winfo_height()
        try:
            image = Image.open(BytesIO(buf))
            self.last_image = image
            image = ImageOps.contain(image, (w, h))
        except Exception as e:
            L().warning(f"Corrupt frame: {str(e)}")
            return
        # Must keep object ref, or it is destroyed immediately.
        self._image = frame["image"] = ImageTk.PhotoImage(image)

    def save(self):
        if self.last_image is None:
            return
        for num in it.count():
            path = Path(f"snapshot{num}.jpg")
            if not path.exists():
                self.last_image.save(str(path))
                return

    def close(self):
        # Remove image handler
        self.receiver.__dict__.pop("on_jpg", None)
        super().close()

def main():
    logging.basicConfig(level="WARNING")
    set_toolkit("ttk")
    with receive_maxsee() as receiver:
        MaxSee(receiver).f_show()

if __name__ == "__main__":
    main()