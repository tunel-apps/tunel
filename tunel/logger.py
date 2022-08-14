__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import inspect
import logging as _logging
import os
import platform
import sys
import threading

from rich import print
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table


class ColorizingStreamHandler(_logging.StreamHandler):

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[%dm"
    BOLD_SEQ = "\033[1m"

    colors = {
        "WARNING": YELLOW,
        "INFO": GREEN,
        "DEBUG": BLUE,
        "CRITICAL": RED,
        "ERROR": RED,
    }

    def __init__(self, nocolor=False, stream=sys.stderr, use_threads=False):
        super().__init__(stream=stream)
        self._output_lock = threading.Lock()
        self.nocolor = nocolor or not self.can_color_tty()

    def can_color_tty(self):
        if "TERM" in os.environ and os.environ["TERM"] == "dumb":
            return False
        return self.is_tty and not platform.system() == "Windows"

    @property
    def is_tty(self):
        isatty = getattr(self.stream, "isatty", None)
        return isatty and isatty()

    def emit(self, record):
        with self._output_lock:
            try:
                self.format(record)  # add the message to the record
                self.stream.write(self.decorate(record))
                self.stream.write(getattr(self, "terminator", "\n"))
                self.flush()
            except BrokenPipeError as e:
                raise e
            except (KeyboardInterrupt, SystemExit):
                # ignore any exceptions in these cases as any relevant messages have been printed before
                pass
            except Exception:
                self.handleError(record)

    def decorate(self, record):
        message = record.message
        message = [message]
        if not self.nocolor and record.levelname in self.colors:
            message.insert(0, self.COLOR_SEQ % (30 + self.colors[record.levelname]))
            message.append(self.RESET_SEQ)
        return "".join(message)


class Logger:
    def __init__(self):
        self.logger = _logging.getLogger(__name__)
        self.log_handler = [self.text_handler]
        self.stream_handler = None
        self.printshellcmds = False
        self.quiet = False
        self.logfile = None
        self.last_msg_was_job_info = False
        self.logfile_handler = None
        self.c = Console()

    def purple(self, msg):
        self.c.print("[bold purple]%s" % msg)

    def cyan(self, msg):
        self.c.print("[bold cyan]%s" % msg)

    def panel_group(self, msgs):
        """
        Input is a dictionary of colors (for panel background) and corresponding messages.
        """
        panels = [Panel(v, style="on %s" % k) for k, v in msgs.items()]
        panel_group = Group(*panels)
        print(Panel(panel_group))

    def cleanup(self):
        if self.logfile_handler is not None:
            self.logger.removeHandler(self.logfile_handler)
            self.logfile_handler.close()
        self.log_handler = [self.text_handler]

    def handler(self, msg):
        for handler in self.log_handler:
            handler(msg)

    def set_stream_handler(self, stream_handler):
        if self.stream_handler is not None:
            self.logger.removeHandler(self.stream_handler)
        self.stream_handler = stream_handler
        self.logger.addHandler(stream_handler)

    def set_level(self, level):
        self.logger.setLevel(level)

    def location(self, msg):
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        self.debug(
            "{}: {info.filename}, {info.function}, {info.lineno}".format(msg, info=info)
        )

    def info(self, msg):
        self.handler(dict(level="info", msg=msg))

    def warning(self, msg):
        self.handler(dict(level="warning", msg=msg))

    def debug(self, msg):
        self.handler(dict(level="debug", msg=msg))

    def error(self, msg):
        self.handler(dict(level="error", msg=msg))

    def exit(self, msg, return_code=1):
        self.handler(dict(level="error", msg=msg))
        sys.exit(return_code)

    def progress(self, done=None, total=None):
        self.handler(dict(level="progress", done=done, total=total))

    def shellcmd(self, msg):
        if msg is not None:
            msg = dict(level="shellcmd", msg=msg)
            self.handler(msg)

    def print_pretty(self, obj):
        """
        Print a dict (and nested content) pretty.
        """
        for field, content in obj.items():

            self.c.print(Rule(field, style="blue"))
            # If we have a dict, make key value pairs
            if isinstance(content, dict):
                panel = ""
                for i, k in enumerate(content):
                    v = content[k]
                    panel += f"{k}: {v}"
                    if i != len(content) - 1:
                        panel += "\n"
                self.c.print(Panel(panel))

            # If we have a dict, make key value pairs
            elif isinstance(content, list) and isinstance(content[0], str):
                panel = ""
                for i, item in enumerate(content):
                    panel += f"- {item}"
                    if i != len(content) - 1:
                        panel += "\n"
                self.c.print(Panel(panel))

            # List of dicts, assumes same keys
            elif isinstance(content, list) and content and isinstance(content[0], dict):
                table = Table()
                fields = content[0]
                for i, key in enumerate(fields):
                    color = "magenta"
                    if i == 0:
                        color = "cyan"
                    table.add_column(key, style=color)
                count = 0
                for item in content:
                    row = []
                    for k in fields:
                        if k in item:
                            row.append(item[k])
                    table.add_row(*row)
                    count += 1
                self.c.print(table)
            elif field == "examples":
                self.c.print(Panel(Syntax(content, "bash")))
            else:
                self.c.print(Panel(content))

    def text_handler(self, msg):
        """
        The default handler prints output to the console.
        Args:
            msg (dict):     the log message dictionary
        """
        level = msg["level"]
        if level == "info" and not self.quiet:
            self.logger.info(msg["msg"])
        if level == "warning":
            self.logger.warning(msg["msg"])
        elif level == "error":
            self.logger.error(msg["msg"])
        elif level == "debug":
            self.logger.debug(msg["msg"])
        elif level == "progress" and not self.quiet:
            done = msg["done"]
            total = msg["total"]
            p = done / total
            percent_fmt = ("{:.2%}" if p < 0.01 else "{:.0%}").format(p)
            self.logger.info(
                "{} of {} steps ({}) done".format(done, total, percent_fmt)
            )
        elif level == "shellcmd":
            if self.printshellcmds:
                self.logger.warning(msg["msg"])


logger = Logger()


def setup_logger(
    quiet=False,
    printshellcmds=False,
    nocolor=False,
    stdout=False,
    debug=False,
    use_threads=False,
    wms_monitor=None,
):
    # console output only if no custom logger was specified
    stream_handler = ColorizingStreamHandler(
        nocolor=nocolor,
        stream=sys.stdout if stdout else sys.stderr,
        use_threads=use_threads,
    )
    logger.set_stream_handler(stream_handler)
    logger.set_level(_logging.DEBUG if debug else _logging.INFO)
    logger.quiet = quiet
    logger.printshellcmds = printshellcmds
