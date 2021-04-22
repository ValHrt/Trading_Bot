import tkinter as tk
import typing

from interface.styling import *


class StrategyEditor(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._all_contracts = []
        self._all_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h"]

        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        self._add_button = tk.Button(self._commands_frame, text="Add strategy", font=GLOBAL_FONT,
                                     command=self._add_strategy_row, bg=BG_COLOR2, fg=FG_COLOR)
        self._add_button.pack(side=tk.TOP)

        self.body_widgets = dict()

        self._headers = ["Strategy", "Contract", "Timeframe", "Balance %", "TP %", "SL %"]

        self._base_params = [
            {"code_name": "strategy_type", "widget": tk.OptionMenu, "data_type": str,
             "values": ["Technical", "Breakout"], "width": 10},
            {"code_name": "contract", "widget": tk.OptionMenu, "data_type": str, "values": self._all_contracts,
             "width": 15},
            {"code_name": "timeframe", "widget": tk.OptionMenu, "data_type": str, "values": self._all_timeframes,
             "width": 7},
            {"code_name": "balance_pct", "widget": tk.Entry, "data_type": float, "width": 7},
            {"code_name": "take_profit", "widget": tk.Entry, "data_type": float, "width": 7},
            {"code_name": "stop_loss", "widget": tk.Entry, "data_type": float, "width": 7},
            {"code_name": "parameters", "widget": tk.Button, "data_type": float, "text": "Parameters",
             "bg": BG_COLOR2, "command": self._show_popup},
            {"code_name": "activation", "widget": tk.Button, "data_type": float, "text": "OFF",
             "bg": "darkred", "command": self._switch_strategy},
            {"code_name": "delete", "widget": tk.Button, "data_type": float, "text": "X",
             "bg": "darkred", "command": self._delete_row}
        ]

        for idx, h in enumerate(self._headers):
            header = tk.Label(self._table_frame, text=h, bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0, column=idx)

        for h in self._base_params:
            self.body_widgets[h["code_name"]] = dict()
            if h["widget"] == tk.OptionMenu:  # Vidéo 32 : 9mn02 (si code ne fonctionne pas)
                self.body_widgets[h["code_name"] + "_var"] = dict()

        self._body_index = 1

    def _add_strategy_row(self):
        b_index = self._body_index

        self._body_index += 1

    def _delete_row(self):
        return

    def _show_popup(self):
        return

    def _switch_strategy(self):
        return
