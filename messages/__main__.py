"""Entry point into the Messages application.
"""

import argparse
from functools import partial

from .archive import Archive
from .messages import Messages

def main():
  """Runs the Messages CLI main loop.
  """
  parser = argparse.ArgumentParser(description="CLI for Messages.")
  parser.add_argument(
      "destination",
      help="Message destination archive",
      type=partial(Archive.from_user, ex_cls=argparse.ArgumentTypeError))
  parser.add_argument(
      '--merge',
      help="Message source archive(s)",
      action='append',
      type=partial(Archive.from_user, ex_cls=argparse.ArgumentTypeError))
  args = parser.parse_args()
  Messages(args.destination, args.merge).cmdloop()

if __name__ == "__main__":
  main()
