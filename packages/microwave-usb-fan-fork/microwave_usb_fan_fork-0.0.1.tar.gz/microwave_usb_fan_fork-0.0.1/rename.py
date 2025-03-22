#! /usr/bin/env python

import os
from pathlib import Path
from typing import Callable

OLD_PROJECT_NAME = 'ratisbona_template_project'

def backup_and_replace(filepath: Path, replacer: Callable[[str], str]):
    bak_file = filepath.with_suffix('.bak')
    filepath.rename(bak_file)
    with open(bak_file, 'r') as the_input, open(filepath, 'w') as the_output:
        for line in the_input:
            the_output.write(replacer(line))

def curried_replacer(old_name: str, new_name: str):
    def replacer(line: str) -> str:
        return line.replace(old_name, new_name)
    return replacer

def main():
    new_project_name = input('Enter new project name: ')
    
    def curried_backup_and_replace(filepath: Path):
        backup_and_replace(filepath, curried_replacer(OLD_PROJECT_NAME, new_project_name))

    base_dir = Path(__file__).parent
    curried_backup_and_replace(base_dir / 'pyproject.toml')

    src_dir = base_dir / 'src' / OLD_PROJECT_NAME

    curried_backup_and_replace(src_dir / '__init__.py')
    curried_backup_and_replace(src_dir / '__main__.py')
    curried_backup_and_replace(src_dir / 'example.py')

    src_dir.rename(base_dir / 'src' / new_project_name)

if __name__ == '__main__':
    main()

