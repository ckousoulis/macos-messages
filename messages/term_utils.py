"""Terminal utilities specific to message archives.

Creates colored text and helps write Messages output.
"""

from contextlib import contextmanager
import itertools
import readline

FG_COLORS = dict(itertools.chain(
    zip(("black",
         "red",
         "green",
         "yellow",
         "blue",
         "magenta",
         "cyan",
         "white",
        ), range(30, 38)),
    zip(("bright_black",
         "bright_red",
         "bright_green",
         "bright_yellow",
         "bright_blue",
         "bright_magenta",
         "bright_cyan",
         "bright_white",
        ), range(90, 98))))

BG_COLORS = dict((f"on_{key}", val + 10) for key, val in FG_COLORS.items())

ATTRIBUTES = dict(
    zip(("bold",
         "faint",
         "italic",
         "underline",
         "slow_blink",
         "rapid_blink",
         "reverse",
         "conceal",
         "strikethrough",
        ), range(1, 10)))

def colored(text, color=None, on_color=None, attrs=None, escape=False):
  """Wraps text with ANSI escape codes to achieve the desired look.

  Args:
      color: The foreground color.
      on_color: The background color.
      attrs: A list of effects.
      escape: True to escape invisibles (for readline); else False.

  Returns:
      A string with the original text wrapped by escape codes.
  """
  def sgr(*codes):
    return "\x1b[%sm" % ";".join(map(str, codes))
  def esc(text):
    return "\x01%s\x02" % text

  codes = []
  if color:
    codes.append(FG_COLORS[color])
  if on_color:
    codes.append(BG_COLORS[on_color])
  if attrs:
    codes.extend(ATTRIBUTES[attr] for attr in attrs)

  if not escape:
    esc = lambda n: n

  return "%s%s%s" % (esc(sgr(*codes)), text, esc(sgr(0)))

@contextmanager
def readline_disabled():
  """Context manager to temporarily disable readline features.
  """
  readline.set_auto_history(False)
  try:
    yield
  finally:
    readline.set_auto_history(True)

def confirm(text):
  """Presents a yes/no prompt to the user and handles replies.

  Args:
      text: A message string to present before confirmation.

  Returns:
      True if the user confirmed the prompt; else False.
  """
  replies = {
      "yes": True,
      "no": False,
  }

  prompt = "%s (yes/no): " % colored("Are you sure?", "red",
                                     attrs=["bold"], escape=True)
  reply = ""
  with readline_disabled():
    print(text)
    while reply not in replies:
      try:
        reply = input(prompt).casefold()
      except (EOFError, KeyboardInterrupt):
        reply = "no"
        print(reply)

  return replies[reply]
