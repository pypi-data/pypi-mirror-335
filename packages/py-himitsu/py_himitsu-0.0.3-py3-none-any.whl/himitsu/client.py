from enum import Enum
from enum import StrEnum
from xdg import BaseDirectory
import himitsu.query
import os
import socket

class Operation(StrEnum):
    QUERY = "query"
    ADD = "add"
    DEL = "del"

class Flag(Enum):
    DECRYPT = 1
    STRICT = 2

class Status(StrEnum):
    HARD_LOCKED = "hard_locked"
    SOFT_LOCKED = "soft_locked"
    UNLOCKED = "unlocked"

class Client:
    def __init__(self, conn):
        self.conn = conn

    def query(self, operation, query, flags=[]):
        cmd = str(operation)

        flags = [flags] if isinstance(flags, Flag) else flags

        for f in flags:
            if f == Flag.DECRYPT:
                cmd += " -d"
            if f == Flag.STRICT:
                cmd += " -s"

        cmd += " " + str(query)
        cmd += "\n"
        self.conn.sendall(cmd.encode())

        entries = []
        prev = ""
        end = False
        while not end:
            response = prev + self.conn.recv(4096).decode('utf8')
            strentries = response.split("\n")
            if strentries[-1] == "":
                strentries = strentries[:-1]

            if not response.endswith("\n"):
                prev = strentries[-1]
                strentries = strentries[:-1]
            elif strentries[-1] == "end":
                end = True
                strentries = strentries[:-1]

            for strentry in strentries:
                if not strentry.startswith("key "):
                    return Exception("invalid response")

                s = strentry[len("key "):]
                entries.append(himitsu.query.parse_str(s))

        return entries

    def lock(self, soft=False):
        """Locks the himitsu daemon, which removes all values from memory
        
        If soft is provided, the daemon willl keep public attributes.
        """

        cmd = "lock"
        if (soft):
            cmd += " -s"
        cmd += "\n"

        self.conn.sendall(cmd.encode())
        status = self.conn.recv(128)
        if status != b"locked\n":
            raise Exception("invalid response")

    def status(self):
        """Queries the status of the himitsu daemon"""

        self.conn.sendall(b"status\n")
        status = self.conn.recv(128)
        if len(status) == 0:
            raise Exception("connection closed")
        status = status.decode('utf-8')

        if not status.endswith("\n"):
            raise Exception("invalid response")

        parts = status.rstrip("\n").split()
        if len(parts) != 2 or parts[0] != "status":
            raise Exception("invalid response")

        try:
            return Status[parts[1].upper()]
        except KeyError:
            raise Exception("invalid response")

def connect():
    """Connects to the himitsu socket and returns a client object"""

    socketpath = os.path.join(BaseDirectory.get_runtime_dir(), "himitsu")

    conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn.connect(socketpath)

    return Client(conn)


