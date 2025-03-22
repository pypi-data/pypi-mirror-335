from typing import List, Callable
from scope.callgraph.dtos.Definition import Definition
from scope.callgraph.enums.CallTreeType import CallTreeType
from scope.callgraph.dtos.CallStack import CallStack


class CallTree(object):
    def __init__(
        self,
        root_defn: Definition,
        all_defns: List[Definition],
        direction: CallTreeType,
        depth=-1,
    ):
        self.root_defn = root_defn
        self.direction = direction
        self.depth = depth
        self.tree = self._build(all_defns)

    def __len__(self) -> int:
        return len(self.tree)

    def __iter__(self):
        return iter(self.tree)

    def __getitem__(self, index: int) -> CallStack:
        return self.tree[index]

    def _build(self, all_defns: List[Definition]) -> List[CallStack]:
        corpus = {d.id: d for d in all_defns}

        def iterative_dfs(start_ref):
            stack = [(start_ref, [start_ref], set())]
            all_paths = []

            while stack:
                current_ref, current_path, seen = stack.pop()
                if self.depth != -1 and len(current_path) > self.depth:
                    all_paths.append(current_path)
                    continue

                if self.direction == CallTreeType.UP:
                    new_refs = corpus[current_ref.id].referenced_by
                else:
                    new_refs = corpus[current_ref.id].referencing

                unseen_refs = [ref for ref in new_refs if ref.id not in seen]
                if not unseen_refs:
                    all_paths.append(current_path)
                else:
                    for new_ref in unseen_refs:
                        new_seen = seen.copy()
                        new_seen.add(new_ref.id)
                        stack.append((new_ref, current_path + [new_ref], new_seen))

            return all_paths

        if self.direction == CallTreeType.UP:
            initial_refs = self.root_defn.referenced_by
        else:
            initial_refs = self.root_defn.referencing

        all_paths = []
        for ref in initial_refs:
            all_paths.extend(iterative_dfs(ref))

        # Convert references to definitions, then wrap in CallStack
        stacks = [[corpus[ref.id] for ref in path] for path in all_paths]
        return [CallStack(stack, self.direction) for stack in stacks]

    def find(
        self,
        root_cb: Callable[[str, Definition], bool] = lambda x, y: True,
        tail_cb: Callable[[str, Definition], bool] = lambda x, y: True,
    ) -> List[CallStack]:
        matching_stacks = []
        for stack in self.tree:
            if root_cb(stack.root_defn.path, stack.root_defn) and tail_cb(
                stack.root_defn.path, stack.root_defn
            ):
                matching_stacks.append(stack)
        return matching_stacks

    # TODO: flesh out
    def leafs(self):
        return [stack.tail() for stack in self.tree]

    # TODO: flesh out
    def roots(self):
        return [stack.root() for stack in self.tree]
