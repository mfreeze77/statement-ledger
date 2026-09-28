import re
import unicodedata


def tokens(text):
    # Not ASCII-only: keep Unicode letters and normalize apostrophe variants.
    return re.findall(
        r"[^\W_]+(?:['’][^\W_]+)*",
        unicodedata.normalize("NFKC", text).casefold().replace("’", "'"),
        re.UNICODE,
    )
