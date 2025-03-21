import time
import typing
import threading

Style = typing.Literal['ASCII', 'BRAILLE', 'DOTS', 'SCROLL'] | str

Spinners = dict(
    ASCII = '|/-\\',
    BRAILLE = '⣾⣽⣻⢿⡿⣟⣯⣷',
    DOTS = ('', '·', '··', '···'),
    SCROLL = ('.  ', '.. ', '...', ' ..', '  .', '   ')
)

class spin:
    '''
    Represents a Spinner object.
    '''

    def __init__(
        self,
        message: str,
        style: Style = 'BRAILLE',
        exit_message: str = '',
        delay: float = 0.15,
        color: int | str = 36
    ) -> None:
        '''
        Creates a new spinner.

        Example usage:
        ```
        with spin('Spinning'):
            ... # Do slow stuff

        # Optionnaly, interact with the spinner
        with spin('Spinning') as spinner:
            ...
            spinner.exit_message = 'Response: ...'
        ```

        :param message: Message to display while spinning.
        :param style: Spinner style or custom sequence.
        :param exit_message: Message to display after spinning.
        :param delay: Delay between spinner frames.
        :param color: Spinner ANSI color code(s).
        '''

        self.text = message
        self.message = message
        self.style = Spinners.get(style, style)
        self.exit_message = exit_message
        self.delay = delay
        self.color = color

        self.thread: threading.Thread = None
        self.running = threading.Event()
    
    def run(self) -> None:
        '''
        Continously spins.
        '''

        iteration = 0
        while not self.running.is_set():

            print(
                f'\x1b[?25l\x1b[2K\x1b[0m{self.text}'
                f'\x1b[{self.color}m {self.style[iteration % len(self.style)]}\x1b[0m',
                end = '\r'
            )

            iteration += 1
            time.sleep(self.delay)
        
        # Cleanup on exit
        print(f'\x1b[?25l\x1b[2K\x1b[0m{self.message} \x1b[{self.color}m{self.exit_message}\x1b[0m')
    
    def __enter__(self) -> 'spin':
        '''
        Start spinning.
        '''

        self.thread = threading.Thread(target = self.run, daemon = True)
        self.thread.start()
        return self

    def __exit__(self, *a, **kw) -> None:
        '''
        Stop thread.
        '''

        self.running.set()
        # Ensures thread terminates before doing anything else
        self.thread.join()

# EOF