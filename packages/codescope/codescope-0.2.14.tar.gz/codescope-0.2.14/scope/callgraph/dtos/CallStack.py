from typing import List
from scope.callgraph.dtos.Definition import Definition
from scope.callgraph.enums import CallTreeType


class CallStack(object):
    def __init__(self, stack: List[Definition], direction: CallTreeType):
        self.stack = stack
        self.direction = direction

    def __str__(self):
        stack_str = []
        indent_width = 0
        for defn in self.stack:
            stack_str.append(f"{indent_width * ' '}> {defn.pprint()}")
            indent_width += 2
        trace = "\n".join(stack_str)
        root_defn = self.root()
        return f"CallStack(name={root_defn.name}, path={root_defn.path}, direction={self.direction}, id={root_defn.id}):\n{trace}\n"

    def __len__(self) -> int:
        return len(self.stack)

    def slice(self, start: int, end: int) -> "CallStack":
        if start < 0 or end > len(self.stack):
            raise ValueError(f"Invalid slice: start={start}, end={end}")
        return CallStack(self.stack[start:end])

    def root(self) -> Definition:
        return self.stack[0]

    def tail(self) -> Definition:
        return self.stack[-1]
