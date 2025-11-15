"""
Graph implementation for symptom-disease network.
Represents relationships between symptoms and diseases.
"""


class GraphNode:
    """Node in the symptom-disease graph."""
    
    def __init__(self, name, node_type='symptom'):
        self.name = name
        self.type = node_type  # 'symptom' or 'disease'
        self.neighbors = []
    
    def add_neighbor(self, neighbor):
        """Add a neighbor node."""
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)


class SymptomDiseaseGraph:
    """Graph representing symptom-disease relationships."""
    
    def __init__(self):
        """Initialize empty graph."""
        self.nodes = {}  # Dictionary: name -> GraphNode
        self.num_nodes = 0
        self.num_edges = 0
    
    def add_node(self, name, node_type='symptom'):
        """Add a node to the graph."""
        if name not in self.nodes:
            self.nodes[name] = GraphNode(name, node_type)
            self.num_nodes += 1
    
    def add_edge(self, from_node, to_node, bidirectional=True):
        """Add an edge between two nodes."""
        if from_node not in self.nodes:
            self.add_node(from_node, 'symptom')
        if to_node not in self.nodes:
            self.add_node(to_node, 'disease')
        
        self.nodes[from_node].add_neighbor(self.nodes[to_node])
        self.num_edges += 1
        
        if bidirectional:
            self.nodes[to_node].add_neighbor(self.nodes[from_node])
            self.num_edges += 1
    
    def get_neighbors(self, node_name):
        """Get all neighbors of a node."""
        if node_name not in self.nodes:
            return []
        return [neighbor.name for neighbor in self.nodes[node_name].neighbors]
    
    def get_diseases_for_symptom(self, symptom_name):
        """Get all diseases connected to a symptom."""
        diseases = []
        if symptom_name in self.nodes:
            for neighbor in self.nodes[symptom_name].neighbors:
                if neighbor.type == 'disease':
                    diseases.append(neighbor.name)
        return diseases
    
    def get_symptoms_for_disease(self, disease_name):
        """Get all symptoms connected to a disease."""
        symptoms = []
        if disease_name in self.nodes:
            for neighbor in self.nodes[disease_name].neighbors:
                if neighbor.type == 'symptom':
                    symptoms.append(neighbor.name)
        return symptoms
    
    def dfs(self, start_node, visited=None):
        """Depth-First Search from start node."""
        if visited is None:
            visited = set()
        
        if start_node not in self.nodes:
            return []
        
        result = []
        stack = [start_node]
        visited.add(start_node)
        
        while stack:
            current = stack.pop()
            result.append(current)
            
            for neighbor in self.nodes[current].neighbors:
                if neighbor.name not in visited:
                    visited.add(neighbor.name)
                    stack.append(neighbor.name)
        
        return result
    
    def bfs(self, start_node):
        """Breadth-First Search from start node."""
        if start_node not in self.nodes:
            return []
        
        result = []
        visited = set()
        queue = [start_node]
        visited.add(start_node)
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in self.nodes[current].neighbors:
                if neighbor.name not in visited:
                    visited.add(neighbor.name)
                    queue.append(neighbor.name)
        
        return result
    
    def find_path(self, start_node, end_node):
        """Find path between two nodes using BFS."""
        if start_node not in self.nodes or end_node not in self.nodes:
            return None
        
        if start_node == end_node:
            return [start_node]
        
        queue = [(start_node, [start_node])]
        visited = {start_node}
        
        while queue:
            current, path = queue.pop(0)
            
            for neighbor in self.nodes[current].neighbors:
                if neighbor.name == end_node:
                    return path + [neighbor.name]
                
                if neighbor.name not in visited:
                    visited.add(neighbor.name)
                    queue.append((neighbor.name, path + [neighbor.name]))
        
        return None
    
    def get_all_nodes(self):
        """Get all node names."""
        return list(self.nodes.keys())
    
    def get_node_count(self):
        """Get total number of nodes."""
        return self.num_nodes
    
    def get_edge_count(self):
        """Get total number of edges."""
        return self.num_edges
    
    def __str__(self):
        """String representation."""
        result = []
        for node_name, node in self.nodes.items():
            neighbors = [n.name for n in node.neighbors]
            result.append(f"{node_name} ({node.type}): {neighbors}")
        return "\n".join(result)

