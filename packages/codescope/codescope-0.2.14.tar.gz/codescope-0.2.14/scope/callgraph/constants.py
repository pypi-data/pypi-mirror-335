from scope.callgraph.enums import AllowedSymbols

GENERIC_LSP_DEF_SEARCH_ERROR = "Unexpected response from Language Server: None"

TMP_DIR_PARENT = "/tmp/scope/callgraph_root_copies"

STRICT_SYMBOL_TYPES = set(
    [
        "Function",
        "Method",
        "Class",
        "Module",
    ]
)

COMMON_SYMBOL_TYPES = STRICT_SYMBOL_TYPES.union(
    set(
        [
            "Package",
            "Interface",
            "Constructor",
            "Variable",
            "Property",
            "Constant",
            "Enum",
            "Struct",
        ]
    )
)

ALL_SYMBOL_TYPES = COMMON_SYMBOL_TYPES.union(
    set(
        [
            "Namespace",
            "Field",
            "String",
            "Number",
            "Boolean",
            "Array",
            "Object",
            "Key",
            "Null",
            "EnumMember",
            "Event",
            "Operator",
            "TypeParameter",
        ]
    )
)

SYMBOL_PERMISSION_TO_SYMBOL_TYPES = {
    "strict": STRICT_SYMBOL_TYPES,
    "common": COMMON_SYMBOL_TYPES,
    "all": ALL_SYMBOL_TYPES,
}

DEFAULT_SYMBOL_PERMISSION_LEVEL_FOR_LANGUAGE_MAP = {
    "python": AllowedSymbols.STRICT,
    "javascript": AllowedSymbols.COMMON,
    "typescript": AllowedSymbols.COMMON,
    "java": AllowedSymbols.STRICT,
    "rust": AllowedSymbols.STRICT,
    "csharp": AllowedSymbols.STRICT,
    "golang": AllowedSymbols.STRICT,
    "ruby": AllowedSymbols.STRICT,
}

# TODO: Test support for Go, Ruby, Java, Rust, CSharp
LANGUAGE_TO_LSP_LANGUAGE_MAP = {
    "python": "python",
    "javascript": "typescript",
    "typescript": "typescript",
    "java": "java",
    "rust": "rust",
    "csharp": "csharp",
    "golang": "go",
    "ruby": "ruby",
}
