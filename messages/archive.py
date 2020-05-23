"""Archive class representing message archives.

Primary data model and operational logic for message archives.
"""

from datetime import datetime
from pathlib import Path
import re

from messages import file_utils

class Directory:
  """Models a directory of chat files.

  Tracks user changes and handles I/O.

  Attributes:
      pattern: A regex pattern for valid directory names.
      path: A Path object representing the directory.
      chats: A list of Paths for chats originally contained in this directory.
      merges: A list of Paths for chats merged from a source Archive.
      conflicts: A list of Paths for source chats that conflict with these.
      ignores: A list of Paths for source chats to be ignored.
      manual_ignores: A list of Paths the user requests to be ignored.
  """
  pattern = re.compile(r"\d\d\d\d-\d\d-\d\d")

  def __init__(self, path=None):
    """Creates a Directory instance from a path.

    Args:
        path: Path object.
    """
    self.path = path

    if not self.pattern.match(path.name):
      raise ValueError(f"{path} is not a Messages archive directory.")

    self.chats = sorted(self.path.rglob("*.ichat"))
    self.merges = []
    self.conflicts = []
    self.ignores = []
    self.manual_ignores = []

  def chat_for_name(self, other_name):
    """Gets the chat in this directory with the given name.

    Args:
        name: string name from a path.

    Returns:
        A Path object if one matches other_name; else None.
    """
    return next(filter(lambda chat: chat.name == other_name, self.chats), None)

  def merge(self, other_dir):
    """Merges a directory into this Directory instance.

    Args:
        other_dir: The Directory object to merge.
    """
    for other_chat in other_dir.chats:
      chat = self.chat_for_name(other_chat.name)
      if chat:
        statinfo = chat.stat()
        other_statinfo = other_chat.stat()
        if statinfo.st_size == other_statinfo.st_size:
          self.ignores.append(other_chat)
        else:
          self.conflicts.append(other_chat)
      else:
        self.merges.append(other_chat)

  def ignore(self, chat):
    """Sets the given chat to be ignored in this Directory.

    Args:
        chat: A Path object to a chat to ignore.
    """
    def ignore_chat(chats):
      if chat not in chats:
        return False

      chats.remove(chat)
      self.manual_ignores.append(chat)
      return True

    return any(map(ignore_chat, (self.merges, self.conflicts, self.ignores)))

  def flush(self, out, simulate):
    """Writes the changes in this directory to disk.

    Args:
        out: Function to write output.
        simulate: True to simulate the flush but not write.

    Returns:
        The number of chats merged into this directory.
    """
    if not self.merges:
      return 0

    out()

    if self.chats:
      out(f"Entered {self.path}.")
    else:
      if not simulate:
        file_utils.mk_chat_dir(self.path)
      out(f"Created {self.path}.")

    for chat in self.merges:
      if not simulate:
        file_utils.create_chat(self.path / chat.name, source=chat)
      out(f"  Merged {chat}.")

    return len(self.merges)

class Archive:
  """Models a message archive.

  Tracks user changes and handles I/O.

  Attributes:
      path: A Path object representing the archive root.
      directories: A {name: Directory} dictionary.
      sources: A {Path: Archive} dictionary of merged sources.
  """
  @classmethod
  def from_user(cls, archive, ex_cls=ValueError):
    """Creates an Archive instance from user input.

    Args:
        cls: Archive class.
        archive: The relative path given by the user as the root.
        ex_cls: Exception class to raise on error.

    Returns:
        An Archive object.

    Raises:
        ex_cls: The requested root is not a message archive.
    """
    try:
      return cls(archive)
    except ValueError as ex:
      raise ex_cls(ex)

  def __init__(self, archive=None):
    """Initializes an Archive instance.

    Args:
        archive: The relative path given by the user as the root.

    Raises:
        ValueError: The requested root is not a message archive.
    """
    self.path = Path(archive).resolve()
    self.directories = {}
    self.sources = {}

    if not self.path.exists() or not self.path.is_dir():
      raise ValueError(f"{archive} is not a Messages archive.")

    for directory in sorted(filter(lambda d: d.is_dir(), self.path.iterdir())):
      self.directories[directory.name] = Directory(directory)

  def merge(self, other):
    """Merges an archive into this Archive instance.

    Args:
        other: The Archive object to merge.
    """
    if other.path in self.sources:
      raise ValueError(f"{other.path} is already merged.")

    self.sources[other.path] = other

    for name, otherdir in other.directories.items():
      if name not in self.directories:
        self.directories[name] = Directory(self.path / name)
      self.directories[name].merge(otherdir)

    self.directories = (
        {k: self.directories[k] for k in sorted(self.directories)})

  def search(self, word):
    """Searches the archive for chats matching the provided word.

    Args:
        word: A substring to find in the name of archive chats.

    Returns:
        An iterator for Path objects that match the search word.
    """
    results = self.path.rglob(f"*{word}*")
    return sorted(filter(lambda path: path.is_file(), results))

  def ignore(self, chats):
    """Sets each provided chat, if present in this archive, to be ignored.

    Args:
        chats: A list of Path objects from a source archive.

    Returns:
        A list of Path objects which were ignored.
    """
    return [chat for chat in chats if
            self.directories[chat.parent.name].ignore(chat)]

  def can_flush(self):
    """Determines if this Archive instance can be flushed to disk.

    Returns:
        True if there are no conflicts; else False.
    """
    return not any(filter(lambda d: d.conflicts, self.directories.values()))

  def flush(self, out, simulate=False):
    """Writes the changes in this archive to disk.

    Args:
        out: Function to write output.
        simulate: True to simulate the flush but not write.

    Raises:
        ValueError: There are unresolved conflicts.
    """
    if not self.can_flush():
      raise ValueError("Resolve conflicts before flush.")

    out(f"Flushing {self.path} at {datetime.now()}")
    for source in self.sources:
      out(f"  with source {source}")

    merge_count = 0
    for directory in self.directories.values():
      merge_count += directory.flush(out, simulate)

    out()
    out(f"Done! Merged {merge_count} chats.")
