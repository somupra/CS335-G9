class MessageCollector:
    """A collector class that hold compiler messages."""

    def __init__(self):
        self.messages = []
        self.ok = True

    def add(self, message, level="error"):
        """Add a new message to the collector, and print it."""
        if level not in ("error", "warning", "success", "important"):
            raise NotImplementedError

        if level == "error":
            self.ok = False

        cm = CompilerMessage(message=message, level=level)
        self.messages.append(cm)
        print(cm)

    def print(self):
        """Print all the messages in the collector."""

        for message in self.messages:
            print(message)
    


class CompilerMessage(Exception):
    """Custom CompilerMessage exception."""

    def __init__(self, message=None, level="error"):
        self.message = message
        self.level = level

    def __str__(self):
        error = "\x1B[31m"
        warn = "\x1B[33m"
        success = "\x1b[32m"
        important = "\x1b[36m"
        reset = "\x1B[0m"
        bold = "\033[1m"

        if self.level == "warning":
            return f"{bold}{warn}⚠  Warning:{reset} {self.message}"
        if self.level == "success":
            return f"{bold}{success}✔ Success:{reset} {self.message}"
        if self.level == "important":
            return f"{bold}{important}✨ {self.message}{reset}"

        return f"{bold}{error}✖ Error:{reset} {self.message}"


messages = MessageCollector()
