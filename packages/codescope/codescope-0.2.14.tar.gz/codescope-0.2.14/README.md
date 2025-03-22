# Scope

<!--Scope lets you statically extract and query call graphs from a codebase.-->
**A call graph generator designed for codebase RAG.** Uses a combination of LSP and AST parsing to achieve very high accuracy, even for dynamic languages.

* Supports 9+ popular languages
  * JavaScript
  * Python
  * TypeScript
  * Rust
  * C#
  * Java
  * Go
  * Ruby
  * Dart
* Can be used programmatically or via the command-line
* Provides easy retrieval methods (e.g. `definitions()`,  `references()`,  `calltree()`, etc.)


## Install

```bash
> pip install codescope
```

Because Scope uses language-specific LSPs, you'll need to have each language you'd like to parse installed on your machine and in your PATH.

## Usage

### Basic Codebase Q&A with Scope
```python
from scope import CallGraph, repo
from scope.enums.CallTreeType import CallTreeType

# Build a call graph from a directory, it works with multi-language codebases too
cg = CallGraph.build("./my_codebase")

# or call repo
with repo("shobrook", "openlimit") as r:
    cg = CallGraph.build(r.root)

# Save/load call graphs
json_str = cg.json()  # serialize to JSON
cg = CallGraph.from_json(json_str)  # load from JSON

# Get all file paths in the call graph
paths = cg.paths()
# Filter paths with a callback
python_files = cg.paths(lambda path: path.endswith('.py'))

# Get all function/class definitions
definitions = cg.definitions()
# Filter definitions with a callback
class_defs = cg.definitions(lambda path, defn: defn.type == 'class')

# Get all references (function calls)
references = cg.references()
# Filter references with callbacks
filtered_refs = cg.references(
    cb_defn=lambda path, defn: defn.name == 'main',
    cb_ref=lambda path, ref: 'test' not in ref.path
)

# Generate call trees (who calls what)
def_obj = definitions[0]  # get a specific definition
# Get downstream calls (what this function calls)
downstream = cg.calltree(def_obj, CallTreeType.DOWN, depth=2)
# Get upstream calls (who calls this function)
upstream = cg.calltree(def_obj, CallTreeType.UP, depth=2)
```

## Contribution and Development

We welcome PRs! To run tests: ```pytest tests/scope```

## Roadmap

| Category | Feature | Status |
|----------|---------|--------|
| **Performance** | Async multilspy support | In Progress |
| | Tree-sitter fallback for unsupported languages | In Progress |
| | LSP-free fastpath (only tree-sitter) for approximate callgraphs | In Progress |
| | Caching for common operations | In Progress |
| **Core Architecture** | ID-based indexing and serialization | In Progress |
| | Enhanced logging system | In Progress |
| | Pydantic schema migration | Planned |
| **Features** | Incremental graph upserting/updating | Planned |
| | Subgraph extraction | Planned |
| | Definition/Reference deduplication | Planned |
| **Visualization** | GraphViz schema support | Planned |
| | Mermaid schema support | Planned |
| **Documentation** | API documentation | In Progress |
| | CLI documentation | Planned |
| **Tools** | CLI | Planned |
| | Interactive debugging mode | Planned |
| | Standalone server | Planned |
| **Research** | Dataflow diagram extraction | Exploring |
| | Temporal callgraphs | Planned |
| | Filegraphs | In-progress |
| | Evals for RAG Performance | In-progress |


## Limitations

Scope is currently in beta, and we haven't fully optimized the library for indexing performance yet or Callgraph size yet. Larger codebases may take a 30 seconds to a few minutes to index, but you'll need to do that very infrequently. `CallTree` objects are also not true trees, but rather a list of `CallStack` objects, e.g each possible path from the root to the leaf.

We also don't yet support languages like C/C++, Zig, nor do we support common mobile languages like Swift, Kotlin, or Objective-C. Let us know if you'd like support for your language, and we'll prioritize it.

## Acknowledgements

Scope was built in part with the collaboration of Microsoft Research. Adrenaline AI is also contributing to their library, [multilspy](https://github.com/microsoft/multilspy).

```
@inproceedings{NEURIPS2023_662b1774,
 author = {Agrawal, Lakshya A and Kanade, Aditya and Goyal, Navin and Lahiri, Shuvendu and Rajamani, Sriram},
 booktitle = {Advances in Neural Information Processing Systems},
 editor = {A. Oh and T. Naumann and A. Globerson and K. Saenko and M. Hardt and S. Levine},
 pages = {32270--32298},
 publisher = {Curran Associates, Inc.},
 title = {Monitor-Guided Decoding of Code LMs with Static Analysis of Repository Context},
 url = {https://proceedings.neurips.cc/paper_files/paper/2023/file/662b1774ba8845fc1fa3d1fc0177ceeb-Paper-Conference.pdf},
 volume = {36},
 year = {2023}
}
```

## License

Apache 2.0
