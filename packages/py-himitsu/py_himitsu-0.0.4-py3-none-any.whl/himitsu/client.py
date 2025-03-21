from enum import Enum
from enum import StrEnum
from xdg import BaseDirectory
import himitsu.query
import os
import socket

class HimitsuException(Exception):
    def __init__(self, error):
        self.error = error

class Status(StrEnum):
    HARD_LOCKED = "hard_locked"
    SOFT_LOCKED = "soft_locked"
    UNLOCKED = "unlocked"

class Client:
    def __init__(self, conn):
        self.conn = conn

    def query(self, query, strict=False, decrypt=False):
        """Queries himitsu for entries. 'query' may be a himitsu.Query or string."""

        cmd = "query"
        if strict:
            cmd += " -s"
        if decrypt:
            cmd += " -d"

        cmd += " " + str(query)
        cmd += "\n"
        print(cmd)
        self.conn.sendall(cmd.encode())

        return self.__read_keys()

    def add(self, key):
        """Adds a new key to the store. 'key' may be a himitsu.Query or a string."""

        cmd = "add " + str(key) + "\n"
        self.conn.sendall(cmd.encode())

        return self.__read_keys()

    def delete(self, key, strict=True):
        """Deletes a key."""

        cmd = "del"
        if strict:
            cmd += " -s"

        cmd += " " + str(key) + "\n"
        self.conn.sendall(cmd.encode())

        return self.__read_keys()

    def __read_keys(self):
        entries = []
        prev = ""
        end = False
        while not end:
            response = prev + self.conn.recv(4096).decode('utf8')

            self.__check_error(response)

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
                entries.append(himitsu.query.Query(s))

        return entries
    
    def __check_error(self, response):
        if response.startswith("error "):
            raise HimitsuException(response[len("error "):])


    def lock(self, soft=False):
        """Locks the himitsu daemon, which removes all values from memory
        
        If soft is provided, the daemon willl keep public attributes.
        """

        cmd = "lock"
        if (soft):
            cmd += " -s"
        cmd += "\n"

        self.conn.sendall(cmd.encode())
        status = self.conn.recv(128).decode('utf8')

        self.__check_error(status)

        if status != "locked\n":
            raise Exception("invalid response")

    def status(self):
        """Queries the status of the himitsu daemon"""

        self.conn.sendall(b"status\n")
        status = self.conn.recv(128).decode('utf8')

        self.__check_error(status)

        if len(status) == 0:
            raise Exception("connection closed")

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


