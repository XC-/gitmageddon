#!/usr/bin/python3

import os
import subprocess

_INITIAL_WD = os.getcwd()
_INTRO = """
=================================================================================
|                                  GIT UNION                                    |
|                                by Aki Mäkinen                                 |
|                        Distributed under MIT license                          |
|                     https://github.com/XC-/gitmageddon                        |
=================================================================================
"""


class Runner:
    @staticmethod
    def get_cmd(command):
        cmd = None
        if isinstance(command, str):
            cmd = command.split()
        elif isinstance(command, list):
            cmd = command
        else:
            raise TypeError("Unsupported type as command")
        return cmd

    @staticmethod
    def check_call(command):
        cmd = Runner.get_cmd(command)
        return subprocess.check_call(cmd, stderr=subprocess.STDOUT)

    @staticmethod
    def check_output(command):
        cmd = Runner.get_cmd(command)
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT)


print(_INTRO)


try:
    git_is_initiated = Runner.check_output("git status")
except subprocess.CalledProcessError:
    print("Could not find git repository from the working directory.")
    print("Running 'git init'")
    result = Runner.check_call("git init")

try:
    git_status = Runner.check_output("git status").decode("utf-8")
    if "No commits yet" in git_status:
        print("No initial commit found, creating one...")
        with open("{}/dummyfile.delete.me".format(_INITIAL_WD), "a") as dummy:
            dummy.write("Dummy\n")
        Runner.check_output("git add dummyfile.delete.me")
        Runner.check_output(["git", "commit",  "-m",  "'Initial dummy commit'"])
except subprocess.CalledProcessError as e:
    print("Git should be initiated by now. Something went truly south...")
    exit(1)

repositories = {}

print("Define the repositories to combine. End with empty URL definition.")
while True:
    repo_url = input("URL {}: ".format(len(repositories) + 1))
    repo_name = input("Repository name: ")
    if repo_url.strip():
        while True:
            if repo_name in repositories:
                print("Repository name is already in use, please choose a different one: ")
                repo_name = input("Repository name: ")
            else:
                break
        repositories[repo_name] = repo_url
    else:
        break
    print("")

for k, v in repositories.items():
    initial_content = os.listdir(_INITIAL_WD)

    try:
        print("Adding remote {} ({})".format(k, v))
        Runner.check_output("git remote add {} {}".format(k, v))

        print("Fetching master from {}".format(k))
        Runner.check_output("git fetch {} master".format(k))

        print("Merging master")
        Runner.check_output("git merge {}/master --allow-unrelated-histories".format(k))

    except subprocess.CalledProcessError as e:
        print("Failed to get master from {} ({}).".format(k, v))
        raise e

    print("Moving merged files to a separate directory...")
    movable_files = [x for x in os.listdir(_INITIAL_WD) if x not in initial_content]
    os.mkdir("{}/{}".format(_INITIAL_WD, k))
    for f in movable_files:
        os.rename("{}/{}".format(_INITIAL_WD, f), "{}/{}/{}".format(_INITIAL_WD, k, f))

    try:
        print("Commiting file move to git...")
        Runner.check_output("git add .")
        Runner.check_output(["git", "commit", "-m", "'Moved files from {} repository to a separate directory'".format(k)])
    except subprocess.CalledProcessError as e:
        print("Failed to commit file move.")
        raise e


