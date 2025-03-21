import time
import enum
import typing
import threading
import contextlib
from .. import utils

class Spinner(enum.Enum):
    ASCII = '|/-\\'
    BRAILLE = '⣾⣽⣻⢿⡿⣟⣯⣷'
    DOTS = ('','·','··','···')
    SCROLL = ('.  ','.. ','...',' ..','  .','   ')

@contextlib.contextmanager
@utils.ensure('?25h', '0m')
def spin(
    message: str,
    spinner: typing.Literal['ASCII', 'BRAILLE', 'DOTS', 'SCROLL'] | str = 'BRAILLE',
    end_message: str = '',
    delay: float = 0.2,
    color: int | str = 36,
) -> typing.Generator[None, None, None]:
    '''
    A context manager for displaying a long task.

    :param message: Wait message.
    :param spinner: Custom spinner.
    :param frequency: Animation delay.
    :param color: Spinner color.
    '''

    if spinner in Spinner.__members__:
        spinner = Spinner[spinner].value
    
    stop = threading.Event()

    def _run() -> None:
        i = 0
        while not stop.is_set():
            print(f'\x1b[?25l\x1b[2K\x1b[0m{message} \x1b[{color}m{spinner[i % len(spinner)]}\x1b[0m', end = '\r')
            i += 1
            time.sleep(delay)

        # Cleanup
        print(f'\x1b[?25l\x1b[2K\x1b[0m{message} \x1b[{color}m{end_message}\x1b[0m')
    
    thread = threading.Thread(target = _run, daemon = True)
    thread.start()

    try:
        yield
    finally:
        stop.set()
        thread.join()

# EOF