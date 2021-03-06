import copy
from typing import Optional


class Environment:
    def __init__(self, global_env: Optional["Environment"] = None, enclosing: Optional["Environment"] = None):
        if not bool(global_env) == bool(enclosing):
            raise TypeError("An environment has a global environment if and only if it has an enclosing environment")

        if not global_env:
            global_env = self
        self.global_env = global_env
        self.enclosing = enclosing
        self.global_ids = []
        self.values = {}

    @property
    def is_global(self):
        return not self.enclosing

    def add_global(self, *names):
        self.global_ids.extend(names)

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
        if self.is_global:
            self.values[name] = val
        elif name in self.global_ids:
            self.global_env[name] = val
        else:
            self.values[name] = val
