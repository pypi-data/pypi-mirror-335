# Standard library
import uuid
from typing import Dict, List, Any
from dataclasses import dataclass, field

# Local
# from scope.dtos.Symbol import Symbol
from scope.callgraph.dtos.Range import Range
from scope.callgraph.dtos.Reference import Reference
from scope.callgraph.utils import stable_hash

# Third Party
from multilspy import SyncLanguageServer
from loguru import logger


@dataclass
class DefinitionLSP:
    id: str = None
    name: str = ""
    type: str = ""
    path: str = ""
    language: str = ""
    range: Range = Range(-1, -1, -1, -1)
    snippet_range: Range = Range(-1, -1, -1, -1)
    snippet_path: str = ""
    referenced_by: List[Reference] = field(default_factory=list)
    referencing: List[Reference] = field(default_factory=list)
    ingress: bool = False
    egress: bool = False
    external_defs: List[Dict[str, Any]] = field(default_factory=list)
    libraries: bool = False


@dataclass
class DefinitionSerde:
    id: str = None
    name: str = ""
    type: str = ""
    path: str = ""
    language: str = ""
    range: Dict[str, int] = field(default_factory=dict)
    snippet_range: Dict[str, int] = field(default_factory=dict)
    snippet_path: str = ""
    referenced_by: List[Dict[str, Any]] = field(default_factory=list)
    referencing: List[Dict[str, Any]] = field(default_factory=list)
    ingress: bool = False
    egress: bool = False
    external_defs: List[Dict[str, Any]] = field(default_factory=list)
    libraries: bool = False


class Definition(object):
    def __init__(self, defn: DefinitionLSP | DefinitionSerde, **kwargs):
        self.id = defn.id
        self.name = defn.name
        self.type = defn.type
        self.path = defn.path
        self.language = defn.language
        # Identifier range (i.e. `def foo():\n\treturn "bar"` -> range of `def foo():`)
        self.range = defn.range
        # Full range of definition (i.e. range of `def foo():\n\treturn "bar"`)
        self.snippet_range = defn.snippet_range
        self.snippet_path = defn.snippet_path

        # LSP specific
        self.lsp_references: List[Reference] = []

        # for traversing the CG
        self.referenced_by: List[Reference] = defn.referenced_by
        self.referencing: List[Reference] = defn.referencing
        self.aliased_at: List[Reference] = []

        # for linking one callgraph to another
        self.ingress = defn.ingress
        self.egress = defn.egress
        self.external_defs = defn.external_defs

        # NOTE: these need debugging
        # for definitions that map to stdlib or 3rd party libraries
        self.libraries = defn.libraries
        self.error = False

    @classmethod
    def merge_exact(cls, *duplicate_defns: List["Definition"]) -> "Definition":
        """Merge definitions that are exact matches"""
        merged_defn = {}
        for defn in duplicate_defns:
            if not merged_defn:
                merged_defn = defn.to_dict()
                if not isinstance(merged_defn["external_defs"], list):
                    merged_defn["external_defs"] = []
            else:
                external_defs = defn.to_dict().get("external_defs", [])
                for external_def in external_defs:
                    merged_defn["external_defs"].append(external_def)

        # Remove duplicates from external_defs
        merged_defn["external_defs"] = list(set(merged_defn["external_defs"]))

        return cls(lsp_definition=merged_defn)

    def add_external_def(
        self, service_id: str, path: str, identifier: str, line_range: Range
    ):
        """
        Add an external definition to the CallGraph.
        This is a link to another CallGraph, and is used to link definitions across different codebases.
        """
        if not self.external_defs or not isinstance(self.external_defs, list):
            self.external_defs = []
        self.external_defs.append(
            {
                "service_id": service_id,
                "path": path,
                "identifier": identifier,
                "start_line": line_range.start_line,
            }
        )

    def __eq__(self, other):
        if not isinstance(other, (Definition, Reference)):
            return NotImplemented
        return (
            self.name == other.name
            and self.path == other.path
            and self.range == other.range
        )

    def __hash__(self):
        return stable_hash(
            {"name": self.name, "path": self.path, "range": self.range.to_dict()},
            as_int=True,
        )

    def __str__(self) -> str:
        len_ref_by = len(self.referenced_by)
        len_referencing = len(self.referencing)
        return f"Definition(name={self.name}, type={self.type} ident_path={self.path}, ident_range={self.range}, snippet_path={self.snippet_path}, snippet_range={self.snippet_range},  num_ref_by={len_ref_by}, num_referencing={len_referencing} hash={hash(self)})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "language": self.language,
            "range": self.range.to_dict(),
            "snippet_range": self.snippet_range.to_dict(),
            "referenced_by": [ref.to_dict() for ref in self.referenced_by],
            "referencing": [ref.to_dict() for ref in self.referencing],
            "ingress": self.ingress,
            "egress": self.egress,
            "external_defs": self.external_defs,
            "libraries": self.libraries,
        }

    def resolve_references(self, lsp_client: SyncLanguageServer):
        try:
            start_line = self.range.start_line
            start_col = self.range.start_column
            lsp_references = lsp_client.request_references(
                self.path, start_line, start_col
            )
            # Retain all references to this definition, that are not self-referencing or invalid
            for lsp_ref in lsp_references:
                ref_path = lsp_ref.get("absolutePath", "")
                ref_range = Range(
                    lsp_ref.get("range", {}).get("start", {}).get("line", -1),
                    lsp_ref.get("range", {}).get("start", {}).get("character", -1),
                    lsp_ref.get("range", {}).get("end", {}).get("line", -1),
                    lsp_ref.get("range", {}).get("end", {}).get("character", -1),
                )
                same_path_as_defn = ref_path == self.path
                same_range_as_defn = ref_range == self.range
                self_referencing = same_path_as_defn and same_range_as_defn
                if ref_range.invalid() or self_referencing:
                    # print(f"Definition::resolve_references WARN: Invalid reference range for path={ref_path} range={ref_range} | Defn={self.pprint()}")
                    continue
                self.lsp_references.append(Reference.undirected(ref_path, ref_range))
            # logger.warning(f"Definition::resolve_references WARN: References for path={path} startLineCol=[{start_line}:{start_col}], Defn={definition.pprint()} -> references({references})", only=True)
        except Exception as e:
            import traceback

            logger.error(
                f"Definition::resolve_references ERROR: {e} | Path={self.path} | Lines=[{start_line}, {start_col}] | Traceback={traceback.format_exc()}"
            )

    def pprint(self):
        return f"{self.path}<{self.type}:{self.name}>({self.range.start_line}:{self.range.start_column})[refd_by={len(self.referenced_by)}][refs_to={len(self.referencing)}]"

    # TODO: need to figure out a way to pass this typehint for symbol: Symbol. Getting circular import issue otherwise
    @classmethod
    def from_lsp_definition(cls, lsp_definition: dict, symbol):
        # NOTE: Example of what comes back from LSP (python)
        # [{'uri': 'file:///tmp/adrenaline/callgraph_root_copies/706fea2d/app/core/qa/configs/DefaultConfig.py', 'range': {'start': {'line': 4, 'character': 6}, 'end': {'line': 4, 'character': 19}}, 'absolutePath': '/tmp/adrenaline/callgraph_root_copies/706fea2d/app/core/qa/configs/DefaultConfig.py', 'relativePath': 'app/core/qa/configs/DefaultConfig.py'}]
        defn = DefinitionLSP(
            id=str(uuid.uuid4()),
            name=symbol.name,
            type=symbol.type,
            language=symbol.language,
            path=lsp_definition.get("absolutePath", ""),
            range=Range(
                lsp_definition["range"]["start"]["line"],
                lsp_definition["range"]["start"]["character"],
                lsp_definition["range"]["end"]["line"],
                lsp_definition["range"]["end"]["character"],
            ),
            snippet_range=symbol.definition_range,
            snippet_path=symbol.path,
        )
        return cls(defn)

    @classmethod
    def from_dict(cls, serde_definition: dict):
        defn = DefinitionSerde(
            id=serde_definition.get("id"),
            name=serde_definition.get("name"),
            type=serde_definition.get("type"),
            path=serde_definition.get("path"),
            language=serde_definition.get("language"),
            range=Range(**serde_definition.get("range")),
            snippet_range=Range(**serde_definition.get("snippet_range")),
            referenced_by=serde_definition.get("referenced_by"),
            referencing=serde_definition.get("referencing"),
            ingress=serde_definition.get("ingress"),
            egress=serde_definition.get("egress"),
            external_defs=serde_definition.get("external_defs"),
            libraries=serde_definition.get("libraries"),
        )
        return cls(defn)

    @classmethod
    def from_error(cls):
        defn = DefinitionLSP(
            name="",
            type="",
            path="",
            language="",
            range=Range(-1, -1, -1, -1),
            snippet_range=Range(-1, -1, -1, -1),
            snippet_path="",
        )
        new_defn = cls(defn)
        new_defn.error = True
        return new_defn
