"""A module for conealing user password input."""

from curses import initscr, echo, noecho, cbreak, nocbreak, endwin


class ConcealPass(object):
    """Conatin methods for revealed and concealed user password input."""
    __slots__: tuple[str, ...] = ('prompt', 'tty', '__ENTER', '__DELETE')

    def __new__(cls: type['ConcealPass'], prompt: str = "Enter password: ", /) -> 'ConcealPass':
        """Create a new 'ConcealPass' object."""
        assert isinstance(prompt, str), "The 'prompt' parameter must be a string"
        return super(ConcealPass, cls).__new__(cls)

    def __init__(self: 'ConcealPass', prompt: str = "Enter password: ", /) -> None:
        """Initialize 'ConcealPass' instance variables."""
        self.prompt = prompt
        self.tty = None
        self.__ENTER = 10
        self.__DELETE = 127

    def __str__(self: "ConcealPass", /) -> str:
        """Return a string version of the 'ConcealPass' object."""
        return f"ConcealPass(prompt={self.prompt})"

    def __repr__(self: "ConcealPass", /) -> str:
        """Return a representation of the 'ConcealPass' object string."""
        return self.__str__()

    def __dir__(self: 'ConcealPass', /) -> list[str]:
        """List the 'ConcealPass' instance attributes."""
        attrs = list()
        attrs.append('__slots__')
        attrs.append('__new__')
        attrs.append('__init__')
        attrs.append('__str__')
        attrs.append('__repr__')
        attrs.append('__dir__')
        attrs.append('__call__')
        attrs.append('prompt')
        attrs.append('tty')
        attrs.sort()
        return attrs

    def __call__(self: "ConcealPass", /) -> str | None:
        """Allow ConcealPass to be called directly.
        This is the entire ConcealPass implementaition."""
        buffer = list()
        try:
            self.tty = initscr()
            noecho()
            cbreak()
            
            self.tty.addstr(self.prompt)
            while (char := self.tty.getch()) and char != self.__ENTER:
                if char != self.__DELETE:
                    buffer.append(char)
                    self.tty.addch('*')
                elif len(buffer) != 0:
                    y, x = self.tty.getyx()
                    _ = buffer.pop(-1)
                    self.tty.move(y, x - 1)
                    self.tty.delch()
                else:
                    continue
            else:
                self.tty.clear()
                nocbreak()
                echo()
                endwin()
        except (KeyboardInterrupt, ValueError, TypeError):
            nocbreak()
            echo()
            endwin()
            return None
        finally:
            return "".join([chr(c) for c in buffer])
