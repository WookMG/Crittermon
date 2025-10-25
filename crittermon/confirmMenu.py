from pynput import keyboard

import crittermon.tools as tools
from crittermon.tools import clearTerminal

class ConfirmMenu:

    def __init__(self, controller, text, accept, decline):
        self.console = tools.gv.console
        self.input_manager = tools.gv.input_manager
        self.controller = controller
        self.text = text
        self.accept = accept
        self.decline = decline

        self.state = 0
        self.input_manager.changeState(self)
        self.draw()
    
    def draw(self):
        clearTerminal()
        confirm = "[bright_black]Confirm[/bright_black]"
        cancel = "[bright_black]Cancel[/bright_black]"
        
        if self.state:
            cancel = "[bright_white]Cancel <-[bright_white]"
            indent = " " * 9
        else:
            confirm = "[bright_white]Confirm <-[bright_white]"
            indent = " " * 6

        self.console.print(
            f"[bold bright_white]{self.text}[/bold bright_white]\n\n"
            f"{confirm}"
            f"{indent}"
            f"{cancel}"
            )

    def move(self, key):
        if key in ('a', keyboard.Key.left):
            self.state = 0 if self.state != 0 else 1
        elif key in ('d', keyboard.Key.right):
            self.state = 1 if self.state != 1 else 0
        self.draw()
        
    def confirm(self):
        if self.state:
            function = getattr(self.controller, self.decline)
        else:
            function = getattr(self.controller, self.accept)
        function()
    
    def close(self):
        function = getattr(self.controller, self.decline)
        function()
    
    def __str__(self):
        return "confirm"


