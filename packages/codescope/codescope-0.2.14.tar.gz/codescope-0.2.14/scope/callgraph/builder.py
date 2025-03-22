# Standard library
import os
import shutil
import time
from typing import List, Tuple, Any, Dict
from collections import defaultdict

# Local
from scope.callgraph.dtos.Symbol import Symbol
from scope.callgraph.dtos.Definition import Definition
from scope.callgraph.dtos.Reference import Reference
from scope.callgraph.dtos.Alias import Alias
from scope.callgraph.dtos.config.CallGraphBuilderConfig import CallGraphBuilderConfig
from scope.callgraph.enums import ReferenceType
from scope.callgraph.utils import (
    is_file_empty,
    get_all_paths_from_root_relative,
    create_lsp_client_instance,
    convert_to_relative_path,
    get_containing_def_for_ref,
    flatten,
)

# Third party
from loguru import logger


# Main


class CallGraphBuilder(object):
    """
    The CallgraphBuilder is responsible for taking the root path of a service and extracting a callgraph from it.
    Steps:
    1. For every path in the codebase, extract the symbols with the LSP client (e.g. functions, classes, comments, variables, etc.)
    2. For all symbols, find their definitions (with the LSP client) and filter out symbols that we dont care about (e.g. comments, variables, etc.)
    3. For each definition, find all their references (with the LSP client) in the codebase.
    4. Construct the callgraph from the definitions and references as a Dict[str, List[Definition]], where the key is the relative path of the file
    """

    def __init__(self, root_path: str, language: str, config: CallGraphBuilderConfig):
        self.timeit: bool = config.timeit
        self.language: str = language
        self.config: CallGraphBuilderConfig = config

        self.root_path = os.path.abspath(root_path)
        self.all_paths = get_all_paths_from_root_relative(self.root_path)
        self.lsp_client = create_lsp_client_instance(self.root_path, self.language)
        self.abs_paths, self.rel_paths = self.all_paths

        self.symbols = defaultdict(list)
        self.potential_aliases: Dict[str, List[Alias]] = defaultdict(list)
        self.definitions: Dict[str, List[Definition]] = defaultdict(list)

    def find_definitions(
        self,
    ) -> Tuple[Dict[str, List[Definition]], Dict[str, List[Symbol]]]:
        """
        For all paths in a codebase, resolve all symbols, and then for each symbol, find its definition.
        If the definition is an error, we will still add the symbol to the potential_aliases list.
        The alias list is used to sidestep limitations in certain LSP implementations that are less capable of resolving aliased imports.
        """
        time_start = time.time()
        defs_map, potential_aliases = defaultdict(list), defaultdict(list)

        # ask lsp_client to get all symbols in the codebase, then get their definitions via their identifier ranges
        with self.lsp_client.start_server():
            for path in self.abs_paths:
                try:
                    if is_file_empty(path):
                        logger.warning(
                            f"CallGraphBuilder::find_definitions WARN: {path} | is_file_empty=True"
                        )
                        continue
                    symbol_list, _ = self.lsp_client.request_document_symbols(path)
                    symbols = [
                        Symbol(self.root_path, path, self.language, s)
                        for s in symbol_list
                    ]
                    self.symbols[path].extend(symbols)
                    defns = [
                        (s, s.to_definition(path, self.lsp_client))
                        for s in symbols
                        if s.valid(self.config)
                    ]
                    # NOTE: Aliasing temporarily disabled
                    # potential_aliases[path] = [
                    #     Alias(s, self.lsp_client) for s, d in defns if d.error
                    # ]
                    defns = list({d for _, d in defns if not d.error})
                    defs_map[path] = defns
                except Exception as e:
                    import traceback

                    logger.error(
                        f"CallGraphBuilder::find_definitions ERROR: {e} | Path={path} | Traceback={traceback.format_exc()}"
                    )

        # UNUSED: get all overlapping symbols (this covers multiline imports)
        # overlapping_symbols = defaultdict(list)
        # for path, symbols in raw_symbol_map_dtos.items():
        #     for symbol in symbols:
        #         key = hash((path, symbol.definition_range))
        #         overlapping_symbols[key].append(symbol)

        defs_map = {
            path: [defn for defn in defns if defn.path == defn.snippet_path]
            for path, defns in defs_map.items()
        }

        if self.timeit:
            print(
                f"CallGraphBuilder::find_definitions took {time.time() - time_start} seconds"
            )
        self.potential_aliases = potential_aliases
        self.definitions = defs_map

    def mark_references_for_path(self, path) -> List[Tuple[Definition, Any]]:
        """
        For all definitions in a path, find the encapsulating definition for the given definition (referenced_by), as well as the definition that references the given definition (referencing).
        """
        all_definitions = flatten(self.definitions.values())
        for definition in self.definitions[path]:
            # Get all raw references directly from LSP, turn them into undirected references
            definition.resolve_references(self.lsp_client)
            for lsp_ref in definition.lsp_references:
                # Resolve aliases by find their originating reference(s)
                for alias in self.potential_aliases[lsp_ref.path]:
                    for found_alias in alias.find_root_references(
                        all_definitions, lsp_ref.reference_range
                    ):
                        definition.referenced_by.append(found_alias)

                # Mark all definitions that are referenced by the given definition
                defs_matching_ref_path = [
                    d for d in all_definitions if d.path == lsp_ref.path
                ]
                if defs_matching_ref_path:
                    containing_defn = get_containing_def_for_ref(
                        defs_matching_ref_path, lsp_ref.reference_range
                    )
                    if containing_defn is None:
                        continue
                    ref_dto = Reference.from_def(
                        containing_defn, lsp_ref, ReferenceType.PARENT
                    )
                    if ref_dto:
                        definition.referenced_by.append(ref_dto)

        # Mark all definitions that are referencing another, that are not self-referencing
        for definition in self.definitions[path]:
            for ref in definition.referenced_by:
                defs_matching_ref_path = [d for d in all_definitions if d == ref]
                matching_parent_def = (
                    defs_matching_ref_path[0] if defs_matching_ref_path else None
                )
                if not matching_parent_def:
                    continue
                ref_child_dto = Reference.from_def(definition, ref, ReferenceType.CHILD)
                matching_parent_def.referencing.append(ref_child_dto)

    def mark_references(self):
        """
        For all paths in a codebase, find all references to other definitions in the codebase.
        """
        with self.lsp_client.start_server():
            time_start = time.time()
            for path in self.definitions.keys():
                if is_file_empty(path):
                    logger.warning(
                        f"CallGraphBuilder::mark_references WARN: {path} | not in allowlist or is empty"
                    )
                    continue
                try:
                    self.mark_references_for_path(path)
                except Exception as e:
                    import traceback

                    logger.error(
                        f"CallGraphBuilder::mark_references ERROR path=({path}): {e} | Traceback={traceback.format_exc()}"
                    )
            if self.timeit:
                print(
                    f"CallGraphBuilder::mark_references took {time.time() - time_start} seconds"
                )

    def _cleanup(self):
        try:
            if os.path.exists(self.root_path):
                logger.info(
                    f"CallGraphBuilder::_cleanup INFO: {self.root_path} | exists=True"
                )
                shutil.rmtree(self.root_path)
            pass
        except Exception as e:
            import traceback

            logger.error(
                f"CallGraphBuilder::_cleanup ERROR: {e} | Path={self.root_path} | Traceback={traceback.format_exc()}"
            )

    def generate_callgraph(self) -> Dict[str, List[Definition]]:
        if not self.language:
            raise ValueError("CallGraphBuilderConfig.language is required")

        time_start = time.time()
        # Find all definitions, their aliases, and discover their references
        self.find_definitions()
        # Mark all definitions with parent and child references
        self.mark_references()

        if self.config.retain_symbols:
            # Update symbols
            relative_symbols = defaultdict(list)
            for path, symbols in self.symbols.items():
                relative_path = convert_to_relative_path(self.root_path, path)
                for symbol in symbols:
                    symbol.path = convert_to_relative_path(self.root_path, symbol.path)
                relative_symbols[relative_path].extend(symbols)
            self.symbols = relative_symbols

        # NOTE: generate relative callgraph (this can be removed eventually, assuming each LSP implementation has a relativePath)
        callgraph = defaultdict(list)
        for path, defs in self.definitions.items():
            relative_path = convert_to_relative_path(self.root_path, path)
            for defn in defs:
                defn.path = convert_to_relative_path(self.root_path, defn.path)
                for ref in defn.referenced_by:
                    ref.path = convert_to_relative_path(self.root_path, ref.path)
                for ref in defn.referencing:
                    ref.path = convert_to_relative_path(self.root_path, ref.path)
            callgraph[relative_path].extend(defs)

        self._cleanup()
        if self.timeit:
            print(
                f"CallGraphBuilder::generate_callgraph took {time.time() - time_start} seconds"
            )
        return callgraph
