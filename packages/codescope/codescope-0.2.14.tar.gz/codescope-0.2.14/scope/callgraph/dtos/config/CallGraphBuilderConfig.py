# Standard library
from dataclasses import dataclass, asdict
from scope.callgraph.enums import AllowedSymbols


@dataclass
class CallGraphBuilderConfig:
    """
    Config options for the CallGraphBuilder.
    timeit: bool = False
    log_level: LogLevelLSP = LogLevelLSP.NONE
    log_file: str = None
    allowed_symbols: str = AllowedSymbols.STRICT
    allow_libraries: bool = False
    retain_symbols: bool = False
    """

    timeit: bool = False
    log_file: str = None
    log_level: str = None
    allowed_symbols: str = AllowedSymbols.STRICT
    allow_libraries: bool = False
    retain_symbols: bool = False

    def __post_init__(self):
        pass

    @staticmethod
    def union(
        left_config: "CallGraphBuilderConfig", right_config: "CallGraphBuilderConfig"
    ) -> "CallGraphBuilderConfig":
        """
        Creates a new config that combines values from both configs,
        preferring right_config values when they differ from left_config.
        """

        dict1 = asdict(left_config)
        dict2 = asdict(right_config)

        # prefer dict2 values when they differ from dict1
        merged = {
            key: dict2[key] if dict2[key] != dict1[key] else dict1[key]
            for key in dict1.keys()
        }

        return CallGraphBuilderConfig(**merged)

    def __or__(self, other: "CallGraphBuilderConfig") -> "CallGraphBuilderConfig":
        """Implements self | other. RHS values are preferred when they differ from LHS."""
        if other is None:
            return self
        return CallGraphBuilderConfig.union(self, other)
