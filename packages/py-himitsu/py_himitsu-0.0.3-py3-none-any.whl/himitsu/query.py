import re
import shlex

keyRegex = re.compile('^([-_a-zA-Z]+)([!?]*)$')

class Pair:
    def __init__(self, key, value, private, optional):
        self.key = key
        self.value = value
        self.private = private
        self.optional = optional

    def __str__(self):
        s = self.key
        if self.optional:
            s += "?"
        if self.private:
            s += "!"
        if len(self.value) > 0:
            s += "=" + self.value

        return s

class Query:
    """A himitsu query"""

    def __init__(self, pairs):
        self.pairs = pairs

    def __str__(self):
        s = ""
        for p in self.pairs:
            s += " " + str(p)

        return s.lstrip(" ")

def parse_str(query):
    """Parses a query from given string and returns it as query object.

    Raises a ValueError if key or value contains invalid characters.
    """
    pairs = []
    items = shlex.split(query)

    for item in items:
        if len(item) == 0:
            continue

        parts = item.split("=", 1)
        keyparts = keyRegex.match(parts[0])
        if keyparts is None:
            raise ValueError("invalid key")

        key = keyparts[1]
        optional = False
        private = False

        if len(keyparts.groups()) > 1:
            attrs = keyparts[2]
            optional = attrs.find("?") >= 0
            private = attrs.find("!") >= 0
        
        value = ""
        if len(parts) > 1:
            value = parts[1]

        pairs.append(Pair(key, value, private, optional))

    return Query(pairs)


