from pathlib import Path
from typing import List
from statemachine import State, StateMachine


class PhotoBoothMachine(StateMachine):
    initialization = State(initial=True)
    waiting = State()
    capturing = State()
    processing = State()
    printing = State()

    initialized = initialization.to(waiting)
    registered_input = (
        waiting.to(capturing, cond="if_button_pressed")
        | waiting.to(waiting, unless="if_button_pressed")
    )
    captured = capturing.to(processing)
    processed = processing.to(printing)
    printed = printing.to(waiting)

    def __init__(self):
        super().__init__()

    def if_button_pressed(self, pressed: bool) -> bool:
        return pressed

    def on_captured(self, captures: List[Path]):
        self.captures = captures

    def on_processed(self, processed_image: Path):
        self.processed_image = processed_image
