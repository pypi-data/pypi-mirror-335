# Copyright (c) 2024 iiPython

# Modules
import os
import shutil
import atexit
from pathlib import Path

from . import Plugin

# Handle plugin
class StaticPlugin(Plugin):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.source, self.destination = \
            self.builder.source / "static", self.builder.destination

        # Hooks
        atexit.register(self.ensure_symlink_removal)

    def remove(self, path: Path) -> None:
        if path.is_symlink() or path.is_file():
            return path.unlink(missing_ok = True)

        elif path.is_dir():
            shutil.rmtree(path)

    def on_build(self, dev: bool) -> None:
        if not self.source.is_dir():
            return

        for file in self.source.rglob("*"):
            if not file.is_file():
                continue

            destination = self.destination / file.relative_to(self.source)
            if not file.exists():
                self.remove(destination)
                continue

            if not destination.parent.is_dir():
                destination.parent.mkdir(parents = True)

            if dev:
                if destination.is_symlink():
                    continue

                elif destination.exists():
                    self.remove(destination)

                os.symlink(file, destination)

            else:
                if destination.exists():
                    self.remove(destination)

                (shutil.copytree if file.is_dir() else shutil.copy)(file, destination)

    def ensure_symlink_removal(self) -> None:
        for file in self.destination.rglob("*"):
            if file.is_symlink():
                self.remove(file)

        for file in self.destination.rglob("*"):
            if file.is_dir() and not any([x.is_file() for x in file.rglob("*")]):
                shutil.rmtree(file)
