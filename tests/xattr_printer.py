"""Prints extended attributes.

Helper tool to examine extended attributes and possible values.
"""

from pathlib import Path

import xattr

UNSET = "Unset"
IGN = frozenset((".DS_Store"))

def main(root):
  """Main function of this helper.

  Args:
      root: Path object to root directory.
  """
  results = {
      "com.apple.quarantine": {UNSET: []},
      "com.apple.FinderInfo": {UNSET: []},
  }

  for path in sorted(filter(lambda p: p.name not in IGN, root.glob("**/*"))):
    for attr, store in results.items():
      xpath = xattr.xattr(path)
      if attr in xpath:
        val = xpath.get(attr)
        if val not in store:
          store[val] = []

        store[val].append(path)
      else:
        store[UNSET].append(path)

  for key, store in results.items():
    print()
    print(key)
    for val, paths in store.items():
      print()
      print(val)
      for path in paths:
        print(path.relative_to(root))

if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description="Extended Attribute Printer.")
  parser.add_argument("directory", help="Root directory")
  main(Path(parser.parse_args().directory))
