# Standard Library
import os

# Local
from scope.callgraph.enums import LSPSymbolType
from scope.callgraph.constants import SYMBOL_PERMISSION_TO_SYMBOL_TYPES
from scope.callgraph.dtos.Range import Range
from scope.callgraph.dtos.Definition import Definition
from scope.callgraph.utils import root_contains_path, stable_hash
from scope.callgraph.dtos.config.CallGraphBuilderConfig import CallGraphBuilderConfig

# Third party
from multilspy import SyncLanguageServer
from loguru import logger


class Symbol(object):
    def __init__(self, abs_root_path, path, language, lsp_symbol):
        self.abs_root_path = abs_root_path
        self.path = path
        self.language = language

        self.type = LSPSymbolType(lsp_symbol.get("kind", "")).name
        self.name = lsp_symbol.get("name")
        self.snippet = lsp_symbol.get("snippet")

        # TODO: this needs to be looked at
        match language:
            case "python":
                self.get_ranges(lsp_symbol)
            case "javascript" | "typescript":
                self.get_ranges(lsp_symbol)
            case "ruby":
                self.get_ranges(lsp_symbol)
            case _:
                raise ValueError(f"Unsupported language: {language}")

        self.ref = f"{path}:{self.definition_range.start_line}:{self.definition_range.start_column}"
        self.ref_uri = f"file://{self.ref}"
        self.references = []

    def valid(self, valid_config: CallGraphBuilderConfig = None):
        valid_symbol_set = SYMBOL_PERMISSION_TO_SYMBOL_TYPES[
            valid_config.allowed_symbols.value
        ]
        in_symbol_set = self.type in valid_symbol_set
        in_tree = root_contains_path(self.abs_root_path, self.path)
        if valid_config.allow_libraries:
            return in_symbol_set
        else:
            return in_symbol_set and in_tree

    def get_ranges(self, lsp_symbol):
        if self.language == "ruby":
            location = lsp_symbol.get("location", {})
            self.definition_range = Range(
                location.get("range", {}).get("start", {}).get("line", -1),
                location.get("range", {}).get("start", {}).get("character", -1),
                location.get("range", {}).get("end", {}).get("line", -1),
                location.get("range", {}).get("end", {}).get("character", -1),
            )
            self.name_range = Range(
                location.get("range", {}).get("start", {}).get("line", -1),
                location.get("range", {}).get("start", {}).get("character", -1),
                location.get("range", {}).get("end", {}).get("line", -1),
                location.get("range", {}).get("end", {}).get("character", -1),
            )
            return

        # This works for Python + JS/TS
        self.definition_range = Range(
            lsp_symbol.get("range", {}).get("start", {}).get("line", -1),
            lsp_symbol.get("range", {}).get("start", {}).get("character", -1),
            lsp_symbol.get("range", {}).get("end", {}).get("line", -1),
            lsp_symbol.get("range", {}).get("end", {}).get("character", -1),
        )
        self.name_range = Range(
            lsp_symbol.get("selectionRange", {}).get("start", {}).get("line", -1),
            lsp_symbol.get("selectionRange", {}).get("start", {}).get("character", -1),
            lsp_symbol.get("selectionRange", {}).get("end", {}).get("line", -1),
            lsp_symbol.get("selectionRange", {}).get("end", {}).get("character", -1),
        )

    def __str__(self) -> str:
        return f"Symbol(path={self.path}, type={self.type}, lang={self.language} name={self.name}, ident_range={self.name_range}, snippet_range={self.definition_range})"

    def __hash__(self):
        return stable_hash(
            {"name": self.name, "path": self.path, "range": self.name_range.to_dict()},
            as_int=True,
        )

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        return (
            self.path == other.path
            and self.name == other.name
            and self.name_range == other.name_range
        )

    def to_dict(self):
        return {
            "path": self.path,
            "type": self.type,
            "language": self.language,
            "name": self.name,
            "snippet_range": self.definition_range.to_dict(),
            "range": self.name_range.to_dict(),
        }

    def to_definition(self, path: str, lsp_client: SyncLanguageServer) -> Definition:
        try:
            start_line = self.name_range.start_line
            if self.language == "ruby":
                start_line += 1
            start_col = self.name_range.start_column
            relative_path = os.path.relpath(path, self.abs_root_path)
            lsp_defn = lsp_client.request_definition(
                relative_path, start_line, start_col
            )
            # TODO: eventually handle multiple defs
            if not lsp_defn:
                return Definition.from_error()
            return Definition.from_lsp_definition(lsp_defn[0], self)
        except Exception as e:
            import traceback

            logger.error(
                f"Symbol.to_definition ERROR: {str(e)} | Path={path} | Symbol.name={self.name} | Range=[{start_line}:{start_col}] | Traceback={traceback.format_exc()}"
            )
            return Definition.from_error()
