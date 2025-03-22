# Standard library
import os
import orjson
from typing import Dict, List, Callable
from collections import defaultdict

# Local
# from scope.callgraph.dtos.Symbol import Symbol
from scope.callgraph.dtos.Definition import Definition
from scope.callgraph.dtos.Reference import Reference
from scope.callgraph.builder import CallGraphBuilder
from scope.callgraph.dtos.config.CallGraphBuilderConfig import CallGraphBuilderConfig
from scope.callgraph.utils import (
    get_node_id_for_viz,
    copy_and_split_root_by_language_group,
)
from scope.callgraph.dtos.CallTree import CallTree
from scope.callgraph.enums.CallTreeType import CallTreeType
from scope.callgraph.constants import DEFAULT_SYMBOL_PERMISSION_LEVEL_FOR_LANGUAGE_MAP

# Third party
from loguru import logger


class CallGraph(object):
    """
    CallGraph Schema
    {
        "file_path": [
            Definition : {
                "name" : str,
                ... ,
                "range" : Range(),
                "referenced_by" : [Reference(), ...]
                "referencing" : [Reference(), ...]
            },
            ...
        ],
        ...
    }
    """

    def __init__(
        self,
        callgraph: Dict[str, List[Dict]],
        symbols: Dict[str, List[Dict]] = defaultdict(list),
        is_dict=False,
        init_calltrees=False,
    ):
        callgraph = (
            self._convert_from_dict_callgraph(callgraph) if is_dict else callgraph
        )
        self.graph: Dict[str, List[Definition]] = callgraph
        self.symbols: Dict[str, List[Dict]] = symbols
        self.cached_calltrees = []
        if init_calltrees:
            self.calltrees()

    # INITIALIZATION CLASS METHODS
    @classmethod
    def build(cls, root_path, config: CallGraphBuilderConfig = None) -> "CallGraph":
        """
        The CallGraph.build() classmethod is responsible for taking the root path of a service and extracting a callgraph from it.
        Steps:
        1. Split the root path into language groups (e.g. python, javascript, etc.) and setup a LSP client for each language group.
            1.1: Each language group is a subset of the original tree structure of the service, containing only files of a certain language.
        2. For each language group (root path) + path in the group, extract the symbols with the LSP client (e.g. functions, classes, comments, variables, etc.)
        3. For all symbols, find their definitions (with the LSP client) and filter out symbols that we dont care about (e.g. comments, variables, etc.)
        4. For each definition, find all their references (with the LSP client) in the codebase.
        5. Construct the callgraph from the definitions and references as a Dict[str, List[Definition]], where the key is the relative path of the file
        """
        callgraph = defaultdict(list)
        symbols = defaultdict(list)
        abs_root_path = os.path.abspath(root_path)
        queue = copy_and_split_root_by_language_group(abs_root_path)
        # TODO: do multiprocessing, if possible
        for path, language in queue:
            try:
                allowed_symbols = DEFAULT_SYMBOL_PERMISSION_LEVEL_FOR_LANGUAGE_MAP[
                    language
                ]
                default_config = CallGraphBuilderConfig(allowed_symbols=allowed_symbols)
                _config = default_config | config
                builder = CallGraphBuilder(path, language, _config)
                partial_cg = builder.generate_callgraph()
                for path, defs in partial_cg.items():
                    callgraph[path].extend(defs)
                    if _config.retain_symbols:
                        symbols[path].extend(builder.symbols[path])
            except Exception as e:
                import traceback

                logger.error(
                    f"CallGraphBuilder::generate_callgraph ERROR: {e} | Path={path} | Language={language} | Traceback={traceback.format_exc()}"
                )
        return cls(callgraph, symbols)

    @classmethod
    def from_dict(cls, callgraph: Dict[str, List[Dict]]) -> "CallGraph":
        return cls(callgraph, is_dict=True)

    @classmethod
    def from_json(cls, json_str: str) -> "CallGraph":
        return cls.from_dict(orjson.loads(json_str))

    # BUILT-INS
    def __str__(self):
        num_paths = len(self.graph)
        num_definitions = len(self.definitions())
        num_references = len(self.references())
        return f"CallGraph paths=({num_paths}), definitions=({num_definitions}), references=({num_references})"

    # UTILITY METHODS
    def to_dict(self):
        cg_dict = {}
        for path in self.graph.keys():
            cg_dict[path] = [defn.to_dict() for defn in self.graph[path]]
        # return {"callgraph": cg_dict}
        return cg_dict

    def json(self):
        return orjson.dumps(self.to_dict())

    def _convert_from_dict_callgraph(self, defs_map: dict):
        callgraph = defaultdict(list)
        for path, defns in defs_map.items():
            defns_dtos = [Definition.from_dict(defn) for defn in defns]
            for defn in defns_dtos:
                refs_by = [Reference.from_dict(ref) for ref in defn.referenced_by]
                defn.referenced_by = refs_by
                referencing = [Reference.from_dict(ref) for ref in defn.referencing]
                defn.referencing = referencing
            callgraph[path] = defns_dtos
        return callgraph

    # CLASS METHODS
    @classmethod
    def merge(cls, *callgraphs) -> "CallGraph":
        """
        Merge two or more CallGraph objects.

        :param callgraphs: Two or more CallGraph objects to merge
        :return: A new CallGraph object containing all definitions from the input callgraphs
        """
        merged_graph = {}
        for cg in callgraphs:
            for path, definitions in cg.graph.items():
                if path not in merged_graph:
                    merged_graph[path] = []
                merged_graph[path].extend(definitions)

        # Merge exact definitions
        for path, defns in merged_graph.items():
            exact_matches = defaultdict(list)
            for defn in defns:
                key = (defn.name, defn.path, defn.range)
                exact_matches[key].append(defn)

            merged_defns = []
            for match_group in exact_matches.values():
                if len(match_group) > 1:
                    merged_defn = Definition.merge_exact(*match_group)
                    merged_defns.append(merged_defn)
                else:
                    merged_defns.append(match_group[0])

            merged_graph[path] = merged_defns

        return cls(merged_graph)

    @classmethod
    def update(cls, files: List[str]) -> "CallGraph":
        """
        TODO:Update nodes/edges in the CallGraph, or add new ones.
        Useful for incremental updates to the CallGraph, like when re-indexing a codebase.
        """
        pass

    # BASIC GRAPH TRAVERSAL METHODS

    def paths(self, cb: Callable[[str], bool] = lambda x: True) -> List[str]:
        """
        Return all paths in the CallGraph.
        If a callback is provided, only return paths that satify the boolean condition in the callback.
        """
        return [path for path in self.graph.keys() if cb(path)]

    def definitions(
        self, cb: Callable[[str, Definition], bool] = lambda x, y: True
    ) -> List[Definition]:
        """
        Return all definitions in the CallGraph.
        If a callback is provided, only return definitions that satify the boolean condition in the callback.
        """
        defns = []
        for path, defs in self.graph.items():
            for defn in defs:
                if cb(path, defn):
                    defns.append(defn)

        return defns

    def references(
        self,
        cb_defn: Callable[[str, Definition], bool] = lambda x, y: True,
        cb_ref: Callable[[str, Reference], bool] = lambda x, y: True,
        parent=True,
    ) -> List[Reference]:
        """
        Return all references in the CallGraph.
        If a definition callback is provided, only return references that are associated with definitions that satify the boolean condition in the definition callback.
        If a reference callback is provided, only return references that satify the boolean condition in the reference callback.
        """
        refs = []
        for path, defs in self.graph.items():
            for defn in defs:
                if cb_defn(path, defn):
                    references = defn.referenced_by if parent else defn.referencing
                    for ref in references:
                        if cb_ref(path, ref):
                            refs.append(ref)
        return refs

    # MORE ADVANCED GRAPH TRAVERSAL METHODS

    def calltree(
        self, defn: Definition, direction: CallTreeType, depth=-1
    ) -> List[List[Definition]]:
        """
        Return a call tree for a given definition, which is a N-ary tree of all the possible callstacks starting from the root definition.
        """
        return CallTree(defn, self.definitions(), direction, depth)

    def calltrees(
        self, cb: Callable[[str, Definition], bool] = lambda x, y: True
    ) -> List[CallTree]:
        """
        Return all calltrees in the CallGraph.
        If a callback is provided, only return calltrees that satify the boolean condition in the callback.
        """
        if self.cached_calltrees:
            return self.cached_calltrees
        all_calltrees = []
        for path, defs in self.graph.items():
            for defn in defs:
                if cb(path, defn):
                    codepaths_up = self.calltree(defn, CallTreeType.UP)
                    codepaths_down = self.calltree(defn, CallTreeType.DOWN)
                    all_calltrees.append(codepaths_up)
                    all_calltrees.append(codepaths_down)
        self.cached_calltrees = all_calltrees
        return all_calltrees

    # INTER-CALLGRAPH METHODS

    def add_external_def(
        self, service_id: str, caller_defn: Definition, callee_defn: Definition
    ):
        """
        Add an external definition to the CallGraph.
        This is a link to another CallGraph, and is used to link definitions across different codebases.
        """
        seen = set()
        for path, defs in self.graph.items():
            for _defn in defs:
                if _defn == caller_defn and _defn not in seen:
                    _defn.add_external_def(
                        service_id,
                        callee_defn.path,
                        callee_defn.name,
                        callee_defn.range,
                    )
                    seen.add(_defn)

    # VISUALIZATION METHODS
    def viz_format(self):
        """
        Return the CallGraph in a format that can be used for visualization.
        """
        nodes, edges = [], []
        for _, defs in self.graph.items():
            for defn in defs:
                # Add node
                node = {
                    "id": get_node_id_for_viz(defn),
                    "name": defn.name,
                    "path": defn.path,
                    "type": defn.type,
                    "is_ingress": defn.ingress,
                    "is_egress": defn.egress,
                }
                nodes.append(node)

                # Add edges
                for ref in defn.referenced_by:
                    edge = {
                        "source": get_node_id_for_viz(ref),
                        "target": get_node_id_for_viz(defn),
                    }
                    edges.append(edge)
                for ref in defn.referencing:
                    edge = {
                        "source": get_node_id_for_viz(defn),
                        "target": get_node_id_for_viz(ref),
                    }
                    edges.append(edge)

        return nodes, edges
