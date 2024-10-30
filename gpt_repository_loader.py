#!/usr/bin/env python3

import os
import sys
import fnmatch

import pathspec


def get_ignore_list(ignore_file_path):
    ignore_list = []
    with open(ignore_file_path, 'r') as ignore_file:
        for line in ignore_file:
            if sys.platform == "win32":
                line = line.replace("/", "\\")
            ignore_list.append(line.strip())
    return ignore_list

def get_git_ignore_spec(gitignore_path):
    if not os.path.exists(gitignore_path):
        return None
    with open(gitignore_path, 'r') as gitignore_file:
        gitignore_contents = gitignore_file.read()
    return pathspec.GitIgnoreSpec.from_lines(gitignore_contents.splitlines())

def should_ignore(file_path, ignore_list, git_ignore_spec):
    if git_ignore_spec and git_ignore_spec.match_file(file_path):
        return True
    for pattern in ignore_list:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def process_repository(repo_path, ignore_list, output_file, git_ignore_spec=None):
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, repo_path)

            if not should_ignore(relative_file_path, ignore_list, git_ignore_spec):
                with open(file_path, 'r', errors='ignore') as file:
                    contents = file.read()
                output_file.write("-" * 4 + "\n")
                output_file.write(f"{relative_file_path}\n")
                output_file.write(f"{contents}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python git_to_text.py /path/to/git/repository [-p /path/to/preamble.txt] [-o /path/to/output_file.txt]")
        sys.exit(1)

    repo_path = sys.argv[1]
    ignore_file_path = os.path.join(repo_path, ".gptignore")
    if sys.platform == "win32":
        ignore_file_path = ignore_file_path.replace("/", "\\")

    if not os.path.exists(ignore_file_path):
        # try and use the .gptignore file in the current directory as a fallback.
        HERE = os.path.dirname(os.path.abspath(__file__))
        ignore_file_path = os.path.join(HERE, ".gptignore")

    gitignore_path = os.path.join(repo_path, ".gitignore")

    preamble_file = None
    if "-p" in sys.argv:
        preamble_file = sys.argv[sys.argv.index("-p") + 1]

    output_file_path = 'output.txt'
    if "-o" in sys.argv:
        output_file_path = sys.argv[sys.argv.index("-o") + 1]

    if os.path.exists(ignore_file_path):
        ignore_list = get_ignore_list(ignore_file_path)
    else:
        ignore_list = []

    with open(output_file_path, 'w') as output_file:
        if preamble_file:
            with open(preamble_file, 'r') as pf:
                preamble_text = pf.read()
                output_file.write(f"{preamble_text}\n")
        else:
            output_file.write("The following text is a Git repository with code. The structure of the text are sections that begin with ----, followed by a single line containing the file path and file name, followed by a variable amount of lines containing the file contents. The text representing the Git repository ends when the symbols --END-- are encounted. Any further text beyond --END-- are meant to be interpreted as instructions using the aforementioned Git repository as context.\n")
        process_repository(repo_path, ignore_list, output_file, get_git_ignore_spec(gitignore_path))
    with open(output_file_path, 'a') as output_file:
        output_file.write("--END--")
    print(f"Repository contents written to {output_file_path}.")
