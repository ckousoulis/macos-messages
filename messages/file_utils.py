"""File utilities specific to message archives.

Wraps basic file copy/create to handle extended attribute.
"""

from datetime import date
import shutil
import time

import xattr

DIR_ARGS = {"mode": 0o700}
FILE_ARGS = {"mode": 0o644}

XATTR_FINDER_KEY = "com.apple.FinderInfo"
XATTR_FINDER_VAL = (1<<76).to_bytes(32, "little")

XATTR_QTINE_KEY = "com.apple.quarantine"
XATTR_QTINE_VAL_FMT = "0082;%08x;Messages"
XATTR_QTINE_DIR_VAL = bytes(XATTR_QTINE_VAL_FMT % 0, "ascii")

def mk_chat_dir(path):
  """Creates a directory to contain chats.

  Args:
      path: Path object to the chat directory.
  """
  path.mkdir(**DIR_ARGS)
  xattr.setxattr(path, XATTR_QTINE_KEY, XATTR_QTINE_DIR_VAL)

def get_qtine_val(path):
  """Generates a quarantine value specific to the given chat.

  Args:
      path: Path object to the chat file.

  Returns:
      bytes to use as quarantine extended attribute.
  """
  chat_date = date.fromisoformat(path.parent.name)
  chat_time = int(time.mktime(chat_date.timetuple()))

  return bytes(XATTR_QTINE_VAL_FMT % chat_time, "ascii")

def create_chat(path, source=None):
  """Creates a chat file with appropriate (extended) attributes.

  Args:
      path: Path object to the chat file.
      source: Path to source file to copy.
  """
  if source:
    shutil.copy(source, path)

  path.touch(**FILE_ARGS)
  xattr.setxattr(path, XATTR_QTINE_KEY, get_qtine_val(path))
  xattr.setxattr(path, XATTR_FINDER_KEY, XATTR_FINDER_VAL)
