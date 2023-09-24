import copy
from typing import Optional

from simplify.utils import eq_nodes


class Scope:
    def __init__(self, global_scope: Optional["Scope"] = None, enclosing: Optional["Scope"] = None):
        if not bool(global_scope) == bool(enclosing):
            raise TypeError("A scope has a global scope if and only if it has an enclosing scope")

        if not global_scope:
            global_scope = self
        self.global_scope = global_scope
        self.enclosing = enclosing

        self.global_ids = []
        self.values = {}

    @property
    def is_global(self):
        return not self.enclosing

    def add_global(self, *names):
        self.global_ids.extend(names)

    def del_scope(self, name):
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

    def __eq__(self, other: "Scope"):
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
            self.global_scope[name] = val
        else:
            self.values[name] = val
