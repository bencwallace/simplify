import copy
from typing import Optional


class Environment:
    def __init__(self, enclosing: Optional["Environment"] = None):
        self.enclosing = enclosing
        self.values = {}
        self.globals = []

    def add_global(self, *names):
        self.globals.extend(names)

    def flatten(self) -> dict:
        if not self.enclosing:
            result = self.values
        else:
            result = self.enclosing.flatten()
            result.update(self.values)
        return copy.copy(result)

    def __contains__(self, name):
        if name in self.values:
            return True
        if self.enclosing:
            return name in self.enclosing
        return False

    def __delitem__(self, name):
        if name in self.values:
            del self.values[name]
        else:
            raise RuntimeError(f"Undefined variable: {name}.")

    def __getitem__(self, name):
        if name in self.values:
            return self.values[name]
        if self.enclosing:
            return self.enclosing[name]
        raise RuntimeError(f"Undefined variable: {name}.")

    def __setitem__(self, name, val):
        self.values[name] = val
