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
    """Creates a himitsu query object. The object acts like a dict. If query
    string is given to the constructor, the query object will be populated with
    its attributes.

    The `str` function can be used to get the query string from a query object.

    Example:
    ```
    q = Query("proto=pass user=someone")
    q["password!"] = "s3cret"
    str(q) == "proto=pass user=someone password!=s3cret"
    ```
    """

    def __init__(self, query=""):
        self.pairs = {}

        items = shlex.split(query)

        for item in items:
            if len(item) == 0:
                continue

            parts = item.split("=", 1)

            key = parts[0]
            value = "" if len(parts) == 1 else parts[1]

            self[key] = value

    def __str__(self):
        s = ""
        for p in self.pairs.values():
            s += " " + str(p)

        return s.lstrip(" ")

    def __repr__(self):
        return "{}('{}')".format(type(self).__name__, str(self))

    def __len__(self):
        return len(self.pairs)

    def __setitem__(self, key, value):
        p = self.__parsekey(key)
        p.value = value
        self.pairs[p.key] = p

    def __parsekey(self, key):
        keyparts = keyRegex.match(key)
        if keyparts is None:
            raise ValueError("invalid key")

        key = keyparts[1]
        optional = False
        private = False

        if len(keyparts.groups()) > 1:
            attrs = keyparts[2]
            optional = attrs.find("?") >= 0
            private = attrs.find("!") >= 0
        
        return Pair(key, None, private=private, optional=optional)

    def __getitem__(self, key):
        p = self.__parsekey(key)
        return self.pairs[p.key].value

    def __iter__(self):
        return self.pairs.__iter__()

    def __contains__(self, key):
        return key in self.pairs

    def __delitem__(self, key):
        p = self.__parsekey(key)
        del self.pairs[p.key]

    def pairs(self):
        return self.pairs.values()
