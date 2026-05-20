import argparse
import getpass
from mcv import MCVParser

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCV Parser login")
    parser.add_argument("-u", "-s", "--username", "--student-id", help="Student ID (10 digits)", dest="username")
    parser.add_argument("-p", "--password", help="Password")
    args = parser.parse_args()

    username = args.username or input("Student ID (10 digits): ")
    password = args.password or getpass.getpass("Password: ")

    mcvp = MCVParser(username, password)

    if mcvp.login():
        mcvp.dump_materials()
    else:
        print("Incorrect username or password")
