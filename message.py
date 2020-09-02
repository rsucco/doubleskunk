from re import compile


# Class for printing messages containing unicode characters with correct space justification
class Message:
    def __init__(self, message=''):
        self.message = message
        self.length = len(message)

    def bare_str(self):
        # Regex to strip color formatting
        REGEX = compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        bare_str = REGEX.sub('', self.message)
        # Convert to ASCII to get rid of the unicode characters
        bare_str = bare_str.encode('ascii', errors='replace')
        return bare_str

    # Generate string left justified, taking ANSI codes and unicode into account
    def ljust(self, width):
        padded_str = self.message
        if len(self.bare_str()) < width:
            for i in range(width - len(self.bare_str()) - 2):
                padded_str += ' '
        return padded_str

    # Generate string centered, taking ANSI codes and unicode into account
    def center(self, width):
        padded_str = self.message
        if len(self.bare_str()) < width:
            # Handle odd numbers
            if (width - len(self.bare_str())) % 2 != 0:
                padded_str += ' '
            else:
                padded_str = ' ' + padded_str + ' '
            for i in range(0, width - len(self.bare_str()) - 2, 2):
                padded_str = ' ' + padded_str + ' '
        return padded_str
