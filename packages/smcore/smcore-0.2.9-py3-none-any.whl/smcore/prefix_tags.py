import re
from typing import Iterable


def extract_prefix_tags(pre: str, tag_list: Iterable[str]):
    # Define a regular expression that matches tags of the form "<pre>: <val>"
    # We will match any expression that is of the above form, and grab the "<val>"
    # as a string in our first *capture group*
    r = re.compile(f"{pre}:\\s(.*)")

    # I know this is not very pythonic, but because
    # it is rather dense, I'd prefer to write it explicitly here
    # so that folks understand clearly how this works if they utilize it
    # and know where to go to get more information:
    #
    # https://docs.python.org/3/library/re.html

    # tags is our final list of values to return, we'll return empty if
    # there are no matches
    tags = []
    for tag in tag_list:
        # Utilize regex group to extract the *value* of any matching prefix tag
        m = r.match(tag)
        if m is not None:
            # group 1 is the parenthesized group here (group 0 is the full match)
            tag_value = m.group(1)
            tags.append(tag_value)

    return tags
