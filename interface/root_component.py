import tkinter as tk
import time

from interface.styling import *
from interface.logging_component import Logging


class Root(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trading Bot")

        self.configure(bg=BG_COLOR)

        self._left_frame = tk.Frame(self, bg=BG_COLOR)
        self._left_frame.pack(side=tk.LEFT)

        self._right_frame = tk.Frame(self, bg=BG_COLOR)
        self._right_frame.pack(side=tk.LEFT)  # LEFT car placé après self.left_frame

        self._logging_frame = Logging(self._left_frame, bg=BG_COLOR)
        self._logging_frame.pack(side=tk.TOP)

        self._logging_frame.add_log("Ceci est un test")
        time.sleep(2)

        self._logging_frame.add_log("Ceci est le test numéro 2")

