# Standard library
from dataclasses import dataclass

# Local
from scope.callgraph.dtos.Range import Range
from scope.callgraph.utils import stable_hash

# from scope.dtos.Definition import Definition
from scope.callgraph.enums import ReferenceType


@dataclass
class ReferenceLSP(object):
    id: str
    name: str
    type: str
    path: str
    language: str
    range: Range
    snippet_range: Range
    reference_range: Range


@dataclass
class ReferenceSerde(object):
    id: str
    name: str
    type: str
    path: str
    language: str
    range: Range
    snippet_range: Range
    reference_range: Range


class Reference(object):
    def __init__(self, ref: ReferenceLSP | ReferenceSerde, **kwargs):
        self.id = ref.id
        self.name = ref.name
        self.type = ref.type
        self.path = ref.path  # File with the containing definition
        self.language = ref.language
        # Identifier range (i.e. `def foo():\n\treturn "bar"` -> range of `def foo():`)
        self.range = ref.range
        # Full range of containing definition (i.e. range of `def foo():\n\tcall_bar()`)
        self.snippet_range = ref.snippet_range
        # Reference range (i.e. `def foo():\n\tcall_bar()` -> range of `call_bar()`)
        self.reference_range = ref.reference_range

        # NOTE: path, range, snippet_range are all attributes of the containing definition

    def __hash__(self):
        return stable_hash(
            {"name": self.name, "path": self.path, "range": self.range.to_dict()},
            as_int=True,
        )

    def __eq__(self, other):
        if not isinstance(other, Reference):
            return NotImplemented

        return self.path == other.path and self.range == other.range

    def __str__(self) -> str:
        return f"Reference(name={self.name} path={self.path}, range={self.range}, ref_range={self.reference_range})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "language": self.language,
            "range": self.range.to_dict(),
            "snippet_range": self.snippet_range.to_dict(),
            "reference_range": self.reference_range.to_dict(),
        }

    # def get_containing_def(self, defs: List[Definition]):
    #     pass

    # def get_containing_ref(self, refs: List["Reference"]):
    #     pass

    @classmethod
    def undirected(cls, path: str, reference_range: Range):
        try:
            ref = ReferenceLSP(
                id=None,
                name=None,
                type=None,
                path=path,
                language=None,
                range=None,
                snippet_range=None,
                reference_range=reference_range,
            )
        except Exception as e:
            print(f"Reference::undirected ERROR: {e}")
            return None
        return cls(ref)

    @classmethod
    # TODO: figure out how to get typehint for defn to map to Definition. Circular import issue
    def from_def(cls, defn: object, partial_ref: "Reference", ref_type: ReferenceType):
        try:
            ref = ReferenceLSP(
                id=defn.id,
                name=defn.name,
                type=ref_type.value,
                path=defn.path,
                language=defn.language,
                range=defn.range,
                snippet_range=defn.snippet_range,
                reference_range=partial_ref.reference_range,
            )
        except Exception:
            return None
        return cls(ref)

    @classmethod
    def from_dict(cls, data: dict):
        ref = ReferenceSerde(
            id=data.get("id"),
            name=data.get("name"),
            type=data.get("type"),
            path=data.get("path"),
            language=data.get("language"),
            range=Range(**data.get("range")),
            snippet_range=Range(**data.get("snippet_range")),
            reference_range=Range(**data.get("reference_range")),
        )
        return cls(ref)
