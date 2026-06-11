import sys
import os

# Redirect/wrap to the main dynamic execute_step_5 logic
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from execute_step_5 import run_step_5

if __name__ == "__main__":
    run_step_5()
