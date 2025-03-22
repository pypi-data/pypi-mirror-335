import json
from collections import defaultdict
from rustworkx import PyDiGraph
from scope.callgraph.api import CallGraph


class FileGraph(object):
    def __init__(self, callgraph: CallGraph):
        self.filegraph = self._build(callgraph)
        self.rx_graph = self._build_rx_graph()

    def __str__(self):
        num_nodes = len(self.filegraph.keys())
        num_edges = sum([len(edges) for edges in self.filegraph.values()])
        return f"FileGraph(num_nodes={num_nodes}, num_edges={num_edges})"

    def _build(self, callgraph: CallGraph):
        filegraph = defaultdict(list)
        for defn in callgraph.definitions():
            referenced_by_paths = {ref.path for ref in defn.referenced_by}
            filegraph[defn.path].extend(referenced_by_paths)
        for path in filegraph.keys():
            # remove self-referencing nodes, for now
            unique_paths = list(set(filegraph[path]))
            unique_paths = [p for p in unique_paths if p != path]
            filegraph[path] = unique_paths
        return filegraph

    def _build_rx_graph(self):
        # Create a new directed graph
        graph = PyDiGraph()

        # Create mapping of file paths to node indices
        path_to_index = {}

        # Add all nodes first
        for path in self.filegraph.keys():
            idx = graph.add_node(path)
            path_to_index[path] = idx

        # Add all edges
        for source_file, target_files in self.filegraph.items():
            source_idx = path_to_index[source_file]
            for target in target_files:
                target_idx = path_to_index[target]
                graph.add_edge(source_idx, target_idx, None)

        return graph

    def graphviz(self):
        dot_elements = ["digraph FileGraph {", "    node [shape=box];"]
        # Add all edges
        for source_file, target_files in self.filegraph.items():
            # Clean file paths for graphviz labels
            source_node = source_file.replace("/", "_").replace(".", "_")
            # Add source node with label
            dot_elements.append(f'    {source_node} [label="{source_file}"];')
            # Add edges to all files that reference this one
            for target in target_files:
                target_node = target.replace("/", "_").replace(".", "_")
                dot_elements.append(f"    {source_node} -> {target_node};")
        dot_elements.append("}")
        return "\n".join(dot_elements)

    def cluster(self):
        # Bc we switched off networkx, need to implement our own clustering
        # if not HAS_NETWORKX:
        #     raise ImportError(
        #         "FileGraph.cluster not supported. Please install scope extras w/ pip install codescope[extras]."
        #     )
        # adj_matrix = []
        # for source, target_files in self.filegraph.items():
        #     adj_matrix.append(
        #         [1 if target in target_files else 0 for target in target_files]
        #     )
        # adj_matrix = nx.from_numpy_array(adj_matrix)
        # communities = nx.community.greedy_modularity_communities(adj_matrix)
        # # TODO: revert back to original file paths
        # return communities
        pass

    def mermaid(self):
        pass

    def to_dict(self):
        return self.filegraph

    def json(self):
        return json.dumps(self.to_dict())
