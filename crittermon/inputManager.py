from pynput import keyboard

class InputManager:
    def __init__(self):
        self.state = None
        self.keymaps = {}
        
        # Taken from pynput documentation | starts the input listener
        self.listener = keyboard.Listener(on_press=self.onPress)
        self.listener.daemon = True
        self.listener.start()

    def pause(self):
        if self.listener.running:
            self.listener.stop()

    def unpause(self):
        self.listener = keyboard.Listener(on_press=self.onPress)
        self.listener.daemon = True
        self.listener.start()

    # -------------------- -----
    # State-specific key maps
    # -------------------------
    def _worldKeymap(self):
        return {} if not self.state else {
            'w': lambda: self.state.move('w'),
            'a': lambda: self.state.move('a'),
            's': lambda: self.state.move('s'),
            'd': lambda: self.state.move('d'),
            'm': self.state.openPauseMenu,
            keyboard.Key.up: lambda: self.state.move(keyboard.Key.up),
            keyboard.Key.down: lambda: self.state.move(keyboard.Key.down),
            keyboard.Key.left: lambda: self.state.move(keyboard.Key.left),
            keyboard.Key.right: lambda: self.state.move(keyboard.Key.right),
            keyboard.Key.esc: self.state.openPauseMenu
        }

    def _pauseKeymap(self):
        return {} if not self.state else {
            'w': lambda: self.state.move('w'),
            's': lambda: self.state.move('s'),
            'c': self.state.confirm,
            'm': self.state.close,
            keyboard.Key.up: lambda: self.state.move(keyboard.Key.up),
            keyboard.Key.down: lambda: self.state.move(keyboard.Key.down),
            keyboard.Key.enter: self.state.confirm,
            keyboard.Key.esc: self.state.close
        }

    def _summaryKeymap(self):
        return {} if not self.state else {
            'w': lambda: self.state.move('w'),
            's': lambda: self.state.move('s'),
            'd': lambda: self.state.move('d'),
            'a': lambda: self.state.move('a'),
            'c': self.state.confirm,
            keyboard.Key.up: lambda: self.state.move(keyboard.Key.up),
            keyboard.Key.down: lambda: self.state.move(keyboard.Key.down),
            keyboard.Key.right: lambda: self.state.move(keyboard.Key.right),
            keyboard.Key.left: lambda: self.state.move(keyboard.Key.left),
            keyboard.Key.enter: self.state.confirm,
            keyboard.Key.esc: self.state.close
        }

    def _fightKeymap(self):
        return {} if not self.fight else {}

    def _confirmKeymap(self):
        return {} if not self.state else {
            'a': lambda: self.state.confirm('a'),
            'd': lambda: self.state.confirm('d'),
            keyboard.Key.left: lambda: self.state.move(keyboard.Key.left),
            keyboard.Key.right: lambda: self.state.move(keyboard.Key.right),
            keyboard.Key.enter: self.state.confirm,
            keyboard.Key.esc: self.state.close
        }
        
    # -------------------------
    # Core listener logic
    # -------------------------
    def onPress(self, key):
        if not self.state:
            return  # ignore input if no state is set yet

        # Get keymap dynamically
        keymap = self.keymaps.get(str(self.state))
        if keymap is None:
            # Build keymap on demand
            keymap = getattr(self, f"_{self.state}Keymap")()
            self.keymaps[self.state] = keymap

        try:
            if key.char in keymap:
                keymap[key.char]()
        except AttributeError:
            if key in keymap:
                keymap[key]()

    def changeState(self, new_state):
        if str(new_state) not in ("world", "pause", "summary", "fight", "confirm"):
            raise ValueError(f"Unknown state '{new_state}'")
        self.state = new_state
        # Rebuild keymap when switching
        self.keymaps[str(self.state)] = getattr(self, f"_{str(self.state)}Keymap")()