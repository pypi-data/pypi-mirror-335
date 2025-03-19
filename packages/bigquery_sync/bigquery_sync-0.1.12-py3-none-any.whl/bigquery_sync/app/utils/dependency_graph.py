from bigquery_sync.app.exceptions.exceptions import DependencyError


class DependencyGraph(object):

    def __init__(self, dependency_nodes_dict):
        self.graph = {node: dependency_nodes for node, dependency_nodes in dependency_nodes_dict.items()}

    def topological_sort(self):
        indegrees = {node: 0 for node in self.graph}
        for node in self.graph:
            indegrees[node] = len(self.graph[node])

        nodes_without_indegrees = []
        for node in self.graph:
            if indegrees[node] == 0:
                nodes_without_indegrees.append(node)
        topological_ordering = []

        reverse_graph = {key: [] for key in self.graph.keys()}
        for node, indegree_nodes in self.graph.items():
            for n in indegree_nodes:
                reverse_graph[n].append(node)

        while len(nodes_without_indegrees) > 0:
            node = nodes_without_indegrees.pop()
            topological_ordering.append(node)
            for neighbor in reverse_graph[node]:
                indegrees[neighbor] -= 1
                if indegrees[neighbor] == 0:
                    nodes_without_indegrees.append(neighbor)

        if len(topological_ordering) == len(self.graph):
            return topological_ordering
        else:
            cyclic_nodes = ''
            for node in self.graph.keys()-topological_ordering:
                cyclic_nodes += '        {}\n'.format(node)
            raise DependencyError('There is a cyclic reference detected among the following nodes: \n{}'.format(cyclic_nodes))
