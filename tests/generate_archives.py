"""Generates test data.

Test data is generated into an "archives" directory next to this file.
"""

from pathlib import Path

import lorem

SAME_CHAT_TEXT = lorem.text()
SAME_TEXT = lambda: SAME_CHAT_TEXT
DIFFERENT_TEXT = lorem.text

ARCHIVES = {
    ("destination",): {
        DIFFERENT_TEXT: {
            "2019-12-27": [
                "Mario Mario on 2019-12-27 at 09.27.26.ichat",
            ],
            "2020-01-10": [
                "Luigi Mario on 2019-01-10 at 14.06.11.ichat",
                "Chat with Mario Mario et al on 2019-01-10 at 16.37.16.ichat",
            ],
            "2020-02-03": [
                "Mario Mario on 2020-02-02 at 02.14.04.ichat",
                "Luigi Mario on 2020-02-03 at 21.23.03.ichat",
            ],
            "2020-03-30": [
                "Mario Mario on 2020-03-30 at 17.01.55.ichat",
            ],
        },
    },
    ("alpha",): {
        DIFFERENT_TEXT: {
            "2019-12-13": [
                "Mario Mario on 2019-12-13 at 03.40.11.ichat",
            ],
            "2020-01-10": [
                "Luigi Mario on 2019-01-10 at 11.19.33.ichat",
                "Chat with Mario Mario et al on 2019-01-09 at 16.37.16.ichat",
            ],
            "2020-02-06": [
                "Mario Mario on 2020-02-05 at 01.06.51.ichat",
                "Luigi Mario on 2020-02-06 at 21.19.33.ichat",
            ],
            "2020-03-19": [
                "Mario Mario on 2020-03-19 at 03.47.32.ichat",
            ],
        },
    },
    ("destination", "alpha",): {
        SAME_TEXT: {
            "2020-02-15": [
                "Chat with Mario Mario et al on 2020-02-15 at 15.35.11.ichat",
            ],
        },
    },
    ("beta",): {
        DIFFERENT_TEXT: {
            "2019-12-27": [
                "Peach on 2019-12-27 at 08.20.29.ichat",
            ],
            "2020-01-10": [
                "Chat with Peach et al on 2019-01-09 at 16.37.16.ichat",
            ],
            "2020-02-21": [
                "Mario Mario on 2020-02-21 at 13.13.13.ichat",
                "Peach on 2020-02-21 at 23.00.43.ichat",
            ],
            "2020-03-19": [
                "Mario Mario on 2020-03-19 at 03.47.32.ichat",
            ],
        },
    },
    ("destination", "beta",): {
        SAME_TEXT: {
            "2020-01-26": [
                "Peach on 2020-01-26 at 20.45.32.ichat",
            ],
        },
        DIFFERENT_TEXT: {
            "2020-01-26": [
                "Chat with Peach et al on 2020-01-26 at 07.28.46.ichat",
            ],
        },
    },
}

def main(base_path):
  """Main function of this test utility.

  Args:
      base_path: Path object to root directory for test archives.
  """
  base_path.mkdir(**file_utils.DIR_ARGS)
  for archive_pair, archive_info in ARCHIVES.items():
    for archive in archive_pair:
      archive_path = Path(base_path, archive)
      file_utils.mk_chat_dir(archive_path)
      for get_text_func, archive_contents in archive_info.items():
        for folder, chats in archive_contents.items():
          folder_path = Path(archive_path, folder)
          file_utils.mk_chat_dir(folder_path)
          for chat in chats:
            chat_path = Path(folder_path, chat)
            file_utils.create_chat(chat_path)
            chat_path.write_text(get_text_func())

if __name__ == "__main__":
  import sys
  sys.path.insert(1, str(Path(__file__, "../..").resolve()))

  from messages import file_utils
  file_utils.DIR_ARGS["exist_ok"] = True

  main(Path(__file__).parent / "archives")
