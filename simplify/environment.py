import copy
from typing import Optional

from simplify.utils import eq_nodes


class Environment:
    def __init__(self, global_env: Optional["Environment"] = None, enclosing: Optional["Environment"] = None):
        if not bool(global_env) == bool(enclosing):
            raise TypeError("An environment has a global environment if and only if it has an enclosing environment")

        if not global_env:
            global_env = self
        self.global_env = global_env
        self.enclosing = enclosing

        self.enclosed = {}  # enclosed sub-environments
        self.global_ids = []
        self.values = {}

    @property
    def is_global(self):
        return not self.enclosing

    def add_env(self, name) -> "Environment":
        assert name not in self.enclosed
        self.enclosed[name] = Environment(self.global_env, self)
        return self.enclosed[name]

    def add_global(self, *names):
        self.global_ids.extend(names)

    def del_env(self, name):
        del self.enclosed[name]

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

    def __eq__(self, other: "Environment"):
        if not len(self.values) == len(other.values):
            return False
        for k in self.values:
            if k not in other:
                return False
            if not eq_nodes(self[k], other[k]):
                return False
        if self.enclosing:
            if not other.enclosing:
                return False
            return self.enclosing == other.enclosing
        return set(self.global_ids) == set(other.global_ids)

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
