from typing import Union, Tuple, Optional

from customtkinter import CTkLabel
from customtkinter import CTkButton
from customtkinter import CTkEntry
from customtkinter import CTkInputDialog
from .OverrideParameterMetrics import OverrideParameterMetrics as ListView

class OverrideParameterWindow(CTkInputDialog):
    """
    Dialog with extra window, message, entry widget, cancel and ok button.
    For detailed information check out the documentation.
    """

    def __init__(self, *args,
                 step_index: 0,
                 option_manager: None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        win_width = 400
        win_height = 800
        if screen_width < win_width:
            win_width = screen_width * 0.9

        if screen_height < win_height:
            win_height = screen_height * 0.9

        # Calculate the x and y coordinates to center the window
        x_coord = (screen_width // 2) - (win_width // 2)
        y_coord = (screen_height // 2) - (win_height // 2)

        self.geometry(f"{win_width}x{win_height}+{x_coord}+{y_coord}")
        
        self.step_index = step_index
        self.option_manager = option_manager
        self.bounds = None

    def _create_widgets(self):

        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self.bounds = ListView(
                self, step_index=self.step_index, option_manager=self.option_manager)
        self.bounds.grid(row=0, column=0, columnspan=2, padx=(10, 10),
                    pady=(10, 10), sticky="nsew")
        self.bounds.grid_columnconfigure(0, weight=1)

    def _on_closing(self):
        self.grab_release()
        self.destroy()
