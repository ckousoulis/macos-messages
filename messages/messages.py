"""CLI for manipulating chat message archives.

Command-line tool whose primary purpose is to merge messages from a backup
archive into a current one.
"""

import atexit
from cmd import Cmd
from pathlib import Path
import readline

from messages.archive import Archive
from messages.term_utils import colored, confirm

class Search:
  """Models a user search in a message archive.

  Attributes:
      query: The user's search input.
      results: A list of Path objects that match the query.
  """
  def __init__(self, query=None):
    """Creates Search instance.

  Attributes:
      query: The user's search input.
    """
    self.query = query or ""
    self.results = []

# pylint: disable=no-self-use
class Messages(Cmd):
  """Messages CLI.

  Derives from cmd.Cmd and defines commands.

  Attributes:
      prompt: String to precede CLI input.
      history: Path to CLI history file.
      destination: Archive object for chat destination.
      last_search: Search object representing the last search.
  """
  prompt = "%s " % colored("<messages>", "cyan", attrs=["bold"], escape=True)

  history = Path("~/.messages_history").expanduser()

  def __init__(self, destination=None, sources=None):
    """Creates Messages instance.

    Args:
        destination: Archive object into which chats should be merged.
        sources: A list of Archive objects to use as chat sources.
    """
    super().__init__()

    if not destination:
      raise ValueError("A destination is required.")

    self.destination = destination
    self.last_search = Search()

    for source in sources or []:
      self.destination.merge(source)

  def cmdloop(self):
    """Runs the main loop.

    Handles CLI history and restarting the command prompt.
    """
    readline.set_history_length(1000)
    atexit.register(readline.write_history_file, self.history)
    if self.history.exists():
      readline.read_history_file(self.history)

    while True:
      try:
        super().cmdloop()
        break
      except KeyboardInterrupt:
        print()
        self.emptyline()

  def onecmd(self, line):
    """Executes one command.

    Returns:
        True to stop processing commands; else False.
    """
    try:
      return super().onecmd(line)
    except ValueError as ex:
      print(f"command failed: {ex}")
      return False

  def emptyline(self):
    """Processes an empty command.

    Returns:
        False to continue processing commands.
    """
    return False

  # pylint: disable=invalid-name
  def do_EOF(self, _):
    """Handles end of line.

    Returns:
        True to stop processing commands.
    """
    print()
    return self.onecmd("quit")

  def do_quit(self, _):
    """Handles quitting the CLI.

    Returns:
        True to stop processing commands.
    """
    return True

  def do_merge(self, line):
    """Merges an archive from a relative path as a source.

    Args:
        line: The relative path given by the user as the root.
    """
    self.destination.merge(Archive.from_user(line))
    return self.onecmd("list")

  def do_list(self, _):
    """Shows the opened archives.
    """
    print("%s %s" % (colored("Destination:", "green"), self.destination.path))
    source_text = colored("Sources:", "yellow")
    if not self.destination.sources:
      source_text += " (None)"

    print(source_text)
    for source in self.destination.sources:
      print(f"  {source}")

  @staticmethod
  def print_directory(directory, full):
    """Prints details about a chat directory.

    Args:
        directory: Directory object to print.
        full: True to print all chats; False for limited set.
    """
    def print_chats(chats, padding, label):
      for chat in chats:
        print("%s%s %s" % (" " * padding, label, chat.name))

    padding = 2
    label = ""
    if not directory.chats:
      if directory.merges:
        label += "%s " % colored("+", "yellow")
      elif directory.conflicts:
        label += "%s " % colored("C", "red")
      else:
        label += "%s " % colored("i", "blue")

    print("%s%s%s" % (" " * padding, label, directory.path.name))
    padding *= 2
    if full:
      print_chats(directory.chats, padding, colored("o", "green"))
      print_chats(directory.merges, padding, colored("+", "yellow"))
      print_chats(directory.ignores, padding, colored("i", "blue"))

    print_chats(directory.conflicts, padding, colored("CC", "red"))
    print_chats(directory.manual_ignores, padding, colored("ii", "blue"))

  def do_show(self, _):
    """Shows destination archive details.
    """
    print(f"{self.destination.path}")
    for directory in self.destination.directories.values():
      self.print_directory(directory, full=True)

  def do_diff(self, _):
    """Shows archive details most relevant for merging.
    """
    print(f"{self.destination.path}")
    for directory in self.destination.directories.values():
      if directory.conflicts or directory.manual_ignores:
        self.print_directory(directory, full=False)

  @staticmethod
  def print_search(search, full):
    """Prints details about a user's search.

    Args:
        search: Search object to print.
        full: True to print all results; False for limited set.
    """
    if full:
      for chat in search.results:
        print(chat)

    total_text = colored(f"{len(search.results)} chats", "yellow")
    print(f"{total_text} for '{search.query}'")

  def do_search(self, line):
    """Searches all sources for chats matching the user's input.

    Args:
        line: A substring to use when searching for chats.
    """
    self.last_search = Search(line)

    for source in self.destination.sources.values():
      results = source.search(line)
      results_text = colored(f"{len(results)} chats", "yellow")
      print(f"Found {results_text} in {source.path}")
      self.last_search.results.extend(results)

    self.print_search(self.last_search, full=False)

  def do_results(self, _):
    """Show the results from the last search.
    """
    self.print_search(self.last_search, full=True)

  def do_ignore(self, _):
    """Sets the merge to ignore chats from the last search.
    """
    ignored = self.destination.ignore(self.last_search.results)
    text = "Ignored %s" % colored(f"{len(ignored)} chats", "blue")
    print(f"{text} for '{self.last_search.query}' in {self.destination.path}")

  def do_simulate(self, _):
    """Simulates the flush of the destination archive.
    """
    self.destination.flush(print, simulate=True)

  def do_flush(self, _):
    """Writes the destination archive with its current state of merges.
    """
    if self.destination.can_flush():
      if confirm(f"Flush will modify {self.destination.path}."):
        path = Path.cwd() / "messages_results.txt"
        path.touch()
        with path.open("w") as out:
          self.destination.flush(lambda tx=None: out.write(f"{tx or ''}\n"))
      else:
        print("Canceled flush.")
    else:
      print(f"Resolve conflicts before flushing {self.destination.path}.")
