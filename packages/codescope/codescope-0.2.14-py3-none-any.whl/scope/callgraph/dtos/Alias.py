# Standard
from typing import List

# Local
from scope.callgraph.dtos.Definition import Definition
from scope.callgraph.dtos.Range import Range
from scope.callgraph.dtos.Reference import Reference
from scope.callgraph.dtos.Symbol import Symbol
from scope.callgraph.utils import get_containing_def_for_ref
from scope.callgraph.enums import ReferenceType

# Third Party
from multilspy import SyncLanguageServer
from loguru import logger


class Alias(object):
    def __init__(self, symbol: Symbol, lsp_client: SyncLanguageServer):
        self.alias_symbol = symbol
        self.root_reference_candidates = []
        self.resolved = False
        # self.references : List[Reference] = []
        self._resolve(lsp_client)

    def find_root_references(
        self, defs: List[Definition], valid_range: Range
    ) -> List[Reference]:
        if not self.resolved:
            return []
        matched_alias_refs = []
        for alias_refs in self.root_reference_candidates:
            if not self.alias_symbol.definition_range.contains(valid_range):
                continue
            for alias_ref in alias_refs:
                alias_ref_range = Range(
                    alias_ref.get("range", {}).get("start", {}).get("line", -1),
                    alias_ref.get("range", {}).get("start", {}).get("character", -1),
                    alias_ref.get("range", {}).get("end", {}).get("line", -1),
                    alias_ref.get("range", {}).get("end", {}).get("character", -1),
                )
                alias_ref_path = alias_ref.get("absolutePath", "")
                paths_match = self.alias_symbol.path == alias_ref_path
                valid = (
                    not self.alias_symbol.definition_range.contains(alias_ref_range)
                    and paths_match
                )
                if valid:
                    defs_at_ref_path = [d for d in defs if d.path == alias_ref_path]
                    containing_def = get_containing_def_for_ref(
                        defs_at_ref_path, alias_ref_range
                    )
                    if containing_def:
                        ref_dto = Reference.from_def(
                            containing_def, alias_ref_range, ReferenceType.PARENT
                        )
                        matched_alias_refs.append(ref_dto)
        return matched_alias_refs

    def _resolve(self, lsp_client: SyncLanguageServer):
        try:
            start_line = self.alias_symbol.name_range.start_line
            start_col = self.alias_symbol.name_range.start_column
            lsp_references = lsp_client.request_references(
                self.alias_symbol.path, start_line, start_col
            )
            for lsp_ref in lsp_references:
                ref_path = lsp_ref.get("absolutePath", "")
                ref_range = Range(
                    lsp_ref.get("range", {}).get("start", {}).get("line", -1),
                    lsp_ref.get("range", {}).get("start", {}).get("character", -1),
                    lsp_ref.get("range", {}).get("end", {}).get("line", -1),
                    lsp_ref.get("range", {}).get("end", {}).get("character", -1),
                )
                self.root_reference_candidates.append(
                    Reference.undirected(ref_path, ref_range)
                )
            self.resolved = True
        except Exception as e:
            import traceback

            logger.error(
                f"Alias::_resolve ERROR: {e} | Path={self.symbol.path} | Symbol={self.symbol.name} | Range=[{self.symbol.name_range.start_line}:{self.symbol.name_range.start_column}] | Traceback={traceback.format_exc()}"
            )
