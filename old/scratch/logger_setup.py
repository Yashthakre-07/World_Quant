import sys
import os

class DualWriter:
    def __init__(self, filepath="live_run.txt"):
        self.terminal = sys.stdout
        self.filepath = filepath
    def write(self, message):
        self.terminal.write(message)
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(message)
        except Exception:
            pass
    def flush(self):
        self.terminal.flush()
    def __getattr__(self, attr):
        return getattr(self.terminal, attr)

# Redirect stdout to write to both terminal and live_run.txt
sys.stdout = DualWriter()
