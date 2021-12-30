import copy
from typing import Optional


class Environment:
    def __init__(self, enclosing: Optional["Environment"] = None):
        self.enclosing = enclosing
        self.values = {}

    def flatten(self) -> dict:
        if not self.enclosing:
            result = self.values
        else:
            result = self.enclosing.flatten()
            result.update(self.values)
        return copy.copy(result)

    def set(self, name, val, is_global=False):
        if not is_global or not self.enclosing:
            self.values[name] = val
        else:
            self.enclosing.set(name, val, is_global=True)

    def __contains__(self, name):
        if name in self.values:
            return True
        if self.enclosing:
            return name in self.enclosing
        return False

    def __getitem__(self, name):
        if name in self.values:
            return self.values[name]
        if self.enclosing:
            return self.enclosing[name]
        raise RuntimeError(f"Undefined variable {name}")

    def __setitem__(self, name, val):
        self.set(name, val)
