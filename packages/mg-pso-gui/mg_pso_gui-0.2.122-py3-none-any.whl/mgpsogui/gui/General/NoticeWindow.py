from typing import Union, Tuple, Optional

from customtkinter import CTkLabel
from customtkinter import CTkButton
from customtkinter import CTkEntry
from customtkinter import CTkInputDialog
from customtkinter import CTkTextbox

class NoticeWindow(CTkInputDialog):
    """
    Dialog with extra window, message, entry widget, cancel and ok button.
    For detailed information check out the documentation.
    """

    def __init__(self,
                 message = None,
                 x = 800,
                 y = 800,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        win_width = x
        win_height = y
        if screen_width < win_width:
            win_width = screen_width * 0.9

        if screen_height < win_height:
            win_height = screen_height * 0.9

        # Calculate the x and y coordinates to center the window
        x_coord = (screen_width // 2) - (win_width // 2)
        y_coord = (screen_height // 2) - (win_height // 2)

        self.geometry(f"{win_width}x{win_height}+{x_coord}+{y_coord}")

        self.message = message


    def _create_widgets(self):

        self.grid_columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.textbox = CTkTextbox(self, state="normal")
        self.textbox.grid(row=0, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.textbox.insert("0.0", self.message)
        self.textbox.configure(wrap="word")
        self.textbox.configure(state="disabled")
            
        self._ok_button = CTkButton(master=self,
                                    width=100,
                                    border_width=0,
                                    fg_color=self._button_fg_color,
                                    hover_color=self._button_hover_color,
                                    text_color=self._button_text_color,
                                    text='OK',
                                    command=self._ok_event)
        self._ok_button.grid(row=1, column=0, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew")
        
    def _ok_event(self, event=None):
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self.grab_release()
        self.destroy()