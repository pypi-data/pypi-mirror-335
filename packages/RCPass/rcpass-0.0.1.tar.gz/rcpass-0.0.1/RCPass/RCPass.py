"""A module for user password input."""

from curses import initscr, echo, noecho, cbreak, nocbreak, endwin


class RCPass(object):
    """Conatin methods for revealed and masked user password input."""
    __slots__: tuple[str, ...] = ('prompt', 'mask', 'tty', '__ENTER')

    def __new__(cls: type['RCPass'], /, *, prompt: str = "Enter password: ", mask: bool = False) -> 'RCPass':
        """Create a new 'RCPass' object."""
        assert isinstance(prompt, str), f"The '{prompt}' parameter must be a string"
        assert isinstance(mask, bool), f"The '{mask}' parameter must be a boolean"
        
        cls.__instance = None
        if cls.__instance is not None:
            return cls.__instance
        else:
            cls.__instance = super(RCPass, cls).__new__(cls)
            return cls.__instance

    def __init__(self: 'RCPass', /, *, prompt: str = "Enter password: ", mask: bool = False) -> None:
        """Initialize 'RCPass' instance variables."""
        self.prompt = prompt
        self.mask = mask
        self.tty = None
        self.__ENTER = '\n'

    def __str__(self: "RCPass", /) -> str:
        """Return a string version of the 'RCPass' object."""
        return f"RCPass(prompt={self.prompt}, mask={self.mask})"

    def __repr__(self: "RCPass", /) -> str:
        """Return a representation of the 'RCPass' object string."""
        return self.__str__()

    def __dir__(self: 'RCPass', /) -> list[str]:
        """List the 'RCPass' instance attributes."""
        attrs = list()
        attrs.append('__slots__')
        attrs.append('__new__')
        attrs.append('__init__')
        attrs.append('__str__')
        attrs.append('__dir__')
        attrs.append('__call__')
        attrs.append('prompt')
        attrs.append('mask')
        attrs.append('tty')
        attrs.append('plain')
        attrs.append('masked')
        attrs.sort()
        return attrs

    def revealed(self: "RCPass", /) -> str | None:
        """Display the password in plain text."""
        buffer = list()

        if self.mask is False:
            self.tty = initscr()
            noecho()
            cbreak()
            try:
                self.tty.addstr(self.prompt)
                while (char := self.tty.getch()) and char != self.__ENTER:
                    buffer.append(chr(char))
                    self.tty.addch(chr(char))
                else:
                    nocbreak()
                    echo()
                    endwin()
                    return "".join(buffer)
            except KeyboardInterrupt:
                nocbreak()
                echo()
                endwin()
                return None
        else:
            raise ValueError("The 'mask' parameter must be 'False'")

    def concealed(self: "RCPass", /) -> str | None:
        """Display the password in asterisk form."""
        buffer = list()

        if self.mask is True:
            self.tty = initscr()
            noecho()
            cbreak()
            try:
                self.tty.addstr(self.prompt)
                while (char := self.tty.getch()) and chr(char) != self.__ENTER:
                    buffer.append(chr(char))
                    self.tty.addch('*')
                else:
                    nocbreak()
                    echo()
                    endwin()
                    return "".join(buffer)
            except KeyboardInterrupt:
                nocbreak()
                echo()
                endwin()
                return None
        else:
            raise ValueError("The 'mask' parameter must be 'True'")

    def __call__(self: "RCPass", /) -> str | None:
        """A convienence method for simpler use."""
        if self.mask is False:
            return self.revealed()
        else:
            return self.concealed()
