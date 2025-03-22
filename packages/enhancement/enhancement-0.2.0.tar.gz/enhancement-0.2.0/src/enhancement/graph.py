import contextlib
import sys
import time
from collections import defaultdict
from threading import current_thread
import networkx as nx
import matplotlib.pyplot as plt

class CLEAR(object):
  """Placeholder to use for a cleared value"""

CLEAR = CLEAR()

class GraphState(dict):
    """
    A PayloadCache holds a mapping of Vertex to VertexPayload representing a particular state of this graph
    """
    _next_depth = 0

    def __init__(self, graph):
        super(GraphState, self).__init__()
        self._depth = GraphState._next_depth
        GraphState._next_depth += 1
        self._graph = graph
        self._active_child = None

    def __del__(self):
        GraphState._next_depth -= 1

    @property
    def active_child(self):
        return self._active_child

    @active_child.setter
    def active_child(self, value):
        self._active_child = value

    def copy(self, other=None):
        if other is None:
            other = GraphState(self._graph)
        other.update({vx_id: vx.clone(other) for vx_id, vx in self.items()})
        return other

    def __hash__(self):
        return id(self)
    
    def __eq__(self,other):
        return id(self) == id(other)

class Graph(object):
    def __init__(self) -> None:
        self._state_stacks = defaultdict(lambda: [GraphState(self)])
        self._debug_mode = False
        self._gather_performance = False
        self._timings = defaultdict(list)
        self._nx_graph = nx.DiGraph()  # Initialize NetworkX directed graph

    def is_calculating(self):
        # Check if any vertex in the current state stack is being calculated
        for state in self._state_stack:
            if state.active_child is not None:
                return True
        return False

    @property
    def timings(self):
        return self._timings

    def reset_timings(self):
        self._timings = defaultdict(list)

    @property
    def is_debug_mode(self):
        return self._debug_mode

    @property
    def gather_performance(self):
        return self._gather_performance

    @contextlib.contextmanager
    def time_it(self, obj):
        if self.gather_performance:
            start_time = time.time()
            yield self
            elapsed = time.time() - start_time
            self._timings[obj].append(elapsed)
        else:
            yield self

    @property
    def _state_stack(self):
        return self._state_stacks[current_thread()]

    @property
    def active_state(self):
        return self._state_stack[-1]

    def push_state(self, graph_state):
        if graph_state in self._state_stack:
            raise RuntimeError('Cannot push a GraphState already in the stack')
        parent_cache = self.active_state
        self._state_stack.append(graph_state)
        return parent_cache

    def pop_state(self):
        if len(self._state_stack) == 1:
            raise RuntimeError('Cannot pop the root state')
        return self._state_stack.pop()

    def get_value(self, vertex):
        # If there is a valid active child, add a directed edge
        active_child = self.active_state.active_child
        if active_child:
            if vertex not in active_child.parents:
                active_child.parents.add(vertex)
            if active_child not in vertex.children:
                vertex.children.add(active_child)
        
        payload = self.active_state.get(vertex)
        if payload is None:
            payload = self.active_state.setdefault(vertex, VertexPayload(vertex, self.active_state))
        if payload.is_valid():
            return payload.value

        saved_child = active_child
        try:
            self.active_state.active_child = vertex
            with self.time_it(vertex):
                payload.value = vertex.evaluate()
                # Ensure vertex is added to graph when evaluated
                self._nx_graph.add_node(vertex._id, value=payload.value)
        finally:
            self.active_state.active_child = saved_child
        
        return payload.value

    def _invalidate_children(self, vertex):
        children = set(vertex.children)
        while children:
            child = children.pop()

            payload = self.active_state.get(child)
            if payload is not None and not payload.is_fixed() and payload.is_valid():
                payload.invalidate()
                children.update(child.children)
    
    def is_fixed(self, vertex):
        if vertex in self.active_state and self.is_calculating():
            raise RuntimeError('Graph cannot be modified while its updating its state')

        payload = self.active_state.get(vertex)
        if payload is None:
            payload = self.active_state.setdefault(vertex, VertexPayload(vertex, self.active_state))
        
        return payload.is_fixed()

    def set_value(self, vertex, value):
        if self.is_calculating():
            raise RuntimeError('Graph cannot be modified while its updating its state')
        
        if value == CLEAR:
            self.clear_value(vertex)
        else:
            payload = self.active_state.get(vertex)
            if payload is None:
                payload = self.active_state.setdefault(vertex, VertexPayload(vertex, self.active_state))
            
            if not payload.is_fixed() or payload.value != value:
                payload.fix_value(value)
                self._invalidate_children(vertex)
            return payload.value

    def clear_value(self, vertex):
        if vertex in self.active_state and self.is_calculating():
            raise RuntimeError('Graph cannot be modified while its updating its state')
        
        payload = self.active_state.get(vertex)
        if not payload or not payload.is_fixed():
            raise RuntimeError('Cannot clear a value that has not been set')
        
        del self.active_state[vertex]
        self._invalidate_children(vertex)
      
    def set_diddle(self, vertex, value):
        if vertex in self.active_state and self.is_calculating():
            raise RuntimeError('Graph cannot be modified while its updating its state')
        
        if not isinstance(self.active_state, DiddleScope):
            raise RuntimeError('Cannot diddle value outside of a DiddleScope')

        payload = self.active_state.setdefault(vertex, VertexPayload(vertex, self.active_state))
        if not payload.is_fixed() or payload.value != value:
            payload._value = value
            payload._flags |= (VertexPayload.FIXED | VertexPayload.VALID)
            self._invalidate_children(vertex)
        return payload.value
      
    def clear_diddle(self, vertex):
        if vertex in self.active_state and self.is_calculating():
            raise RuntimeError('Graph cannot be modified while its updating its state')
        if not isinstance(self.active_state, DiddleScope):
            raise RuntimeError('Cannot diddle value outside of a DiddleScope')

        payload = self.active_state.get(vertex)
        if not payload or not payload.is_fixed():
            raise RuntimeError('Cannot clear a diddle that has not been set')
        
        del self.active_state[vertex]
        self._invalidate_children(vertex)

    def to_networkx(self):
        """Convert the current graph state to a NetworkX graph for analysis"""
        self._nx_graph.clear()
        
        # Add all vertices as nodes
        for vertex, payload in self.active_state.items():
            self._nx_graph.add_node(vertex._id, value=payload.value if payload.is_valid() else None)
        
        # Add edges based on parent-child relationships
        for vertex, payload in self.active_state.items():
            vertex = payload.vertex
            for child in vertex.children:
                self._nx_graph.add_edge(vertex._id, child._id)
        
        return self._nx_graph

    def visualize(self, figsize=(10, 8), with_labels=True):
        """Visualize the graph using NetworkX and matplotlib"""
        plt.figure(figsize=figsize)
        graph = self.to_networkx()
        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=with_labels, node_color='lightblue', 
                node_size=1500, arrowsize=20)
        plt.show()

    def get_cycles(self):
        """Detect cycles in the graph"""
        return list(nx.simple_cycles(self.to_networkx()))

    def get_topological_sort(self):
        """Return nodes in topological sort order"""
        try:
            return list(nx.topological_sort(self.to_networkx()))
        except nx.NetworkXUnfeasible:
            raise RuntimeError("Graph contains cycles and cannot be topologically sorted")

    def get_shortest_path(self, source, target):
        """Find shortest path between two vertices"""
        source_id = self.get_vertex_id(source)
        target_id = self.get_vertex_id(target)
        try:
            return nx.shortest_path(self.to_networkx(), source_id, target_id)
        except nx.NetworkXNoPath:
            return None

    def get_all_paths(self, source, target):
        """Find all paths between two vertices"""
        source_id = self.get_vertex_id(source)
        target_id = self.get_vertex_id(target)
        return list(nx.all_simple_paths(self.to_networkx(), source_id, target_id))

    def get_vertex_id(self, vertex):
        """Get the string identifier for a vertex"""
        if isinstance(vertex, str):
            return vertex
        if isinstance(vertex, GraphVertex):
            return vertex._id
        raise ValueError("Input must be either a vertex ID string or GraphVertex object")

    def ensure_vertex_evaluated(self, vertex):
        """Ensure a vertex is evaluated and added to the graph"""
        if isinstance(vertex, GraphVertex):
            self.get_value(vertex)  # This will evaluate the vertex if needed
            for child in vertex.children:
                self.ensure_vertex_evaluated(child)

_graph = Graph()

class VertexPayload(object):
    NONE = 0x0000
    VALID = 0x0001
    FIXED = 0x0002

    def __init__(self, vertex, graph_state, flags=NONE, value=None):
        self._vertex = vertex
        self._graph_state = graph_state
        self._flags = flags
        self._value = value

    @property
    def vertex(self):
        return self._vertex

    @property
    def flags(self):
        return self._flags

    @property
    def graph_state(self):
        return self._graph_state

    @property
    def value(self):
        if not self.is_valid() and not self.is_fixed():
            raise RuntimeError("This node's value needs to be computed or set")
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value
        self._flags |= VertexPayload.VALID
    
    def fix_value(self, value):
        self.value = value
        self._flags |= VertexPayload.FIXED

    def invalidate(self):
        self._flags &= ~VertexPayload.VALID
        self._value = None

    def is_valid(self):
        return bool(self.flags & self.VALID)

    def is_fixed(self):
        return bool(self.flags & self.FIXED)

    def clone(self, graph_state=None):
        return VertexPayload(
            self.vertex,
            graph_state if graph_state is not None else self._graph_state,
            self.flags,
            self._value
        )

class GraphVertex(object):
    """
    A Vertex is a vertex or node on the graph which has an associated "payload" responsible for holding a value. A Vertex is applied to a memeber function of a GraphObject as a method decorator.
    As part of an acyclic directed graph, edges which connect vertices are directed in a parent -> child fashion such that the payload of the child is dependent upon the payload of the parent.
    """

    def __init__(self, obj, func) -> None:
        self._obj = obj
        self._func = func
        self._id = "{}.{}".format(self._obj.__class__.__name__, self._func.__name__)
        self.parents = set()
        self.children = set()
        """
        self._graph = _graph:
        - Dependency Injection:
        By initializing self._graph with _graph, the GraphVertex class is decoupled from the concrete implementation of the Graph class. This means that the GraphVertex class doesn't directly depend on the Graph class, making it more flexible and easier to test.

        - Allows Customization:
        Initializing self._graph with a provided instance (_graph) allows users of the GraphVertex class to supply their own instance of the Graph class if needed. This can be useful in scenarios where different instances of Graph with specific configurations or behaviors are required.

        - Facilitates Reusability:
        By not hardcoding the instantiation of Graph within the GraphVertex class, the class becomes more reusable. It can be used in various contexts where different instances of Graph are required without modifications to the class itself.

        - Promotes Encapsulation:
        This approach encapsulates the responsibility of providing the Graph instance outside the GraphVertex class. It keeps the class focused on its primary responsibility, which is to represent a vertex in the graph, rather than managing the creation of Graph instances.

        In summary, initializing self._graph with _graph rather than Graph() promotes flexibility, reusability, and encapsulation in the design of the GraphVertex class. It allows for easier customization and testing while keeping the class decoupled from specific implementations of the Graph class.
        """
        self._graph = _graph
    
    def __str__(self) -> str:
        return self._id

    __repr__ = __str__

    def __call__(self, *args, **kwargs):
        # This hack allows us to manipulate the stacktrace, effectively removing the graph inner-working from it
        # Note that if an error would stem from the graph, the stacktrace would still be intact
        try:
            value = self._graph.get_value(self)
        except:
            ex_type, ex, ex_tb = sys.exc_info()
            hacked_tb = ex_tb
            for _ in range(3):
                hacked_tb = hacked_tb.tb_next
                if hacked_tb is None:
                    break
            raise ex.with_traceback(hacked_tb or ex_tb)
        if self._graph.is_debug_mode:
            print("{}() -> {}".format(self._id, value))
        return value

    def evaluate(self):
        value = self._func(self._obj)
        if self._graph.is_debug_mode:
            print("{}.evaluate() -> {}".format(self._id, value))
        return value

    def is_fixed(self):
        fixed = self._graph.is_fixed(self)
        if self._graph.is_debug_mode:
            print("{}.is_fixed() -> {}".format(self._id, fixed))
        return fixed

    def set_value(self, value):
        value = self._graph.set_value(self, value)
        if self._graph.is_debug_mode:
            print("{}.set_value() -> {}".format(self._id, value))
        return value

    def clear_value(self):
        self._graph.clear_value(self)
        if self._graph.is_debug_mode:
            print("{}.clear_value() -> {}".format(self._id, CLEAR))

    def set_diddle(self, value):
        value = self._graph.set_diddle(self, value)
        if self._graph.is_debug_mode:
            print("{}.set_diddle() -> {}".format(self._id, value))
        return value
        
    def clear_diddle(self):
        self._graph.clear_diddle(self)
        if self._graph.is_debug_mode:
            print("{}.clear_diddle() -> {}".format(self._id, CLEAR))

class Vertex(object):
    """
    The decorator used to indicator
    """

    def __init__(self, func) -> None:
        self.func = func

class GraphObject(object):
    def __new__(cls, *args, **kwargs):
        """
        We control here the creation of the GraphObject. All the magic here happens as follows.
        We scan the class for Vertex and replace them on-the-fly with GraphVertex objects that 
        are directly bound to the instance of the GraphObject we created.
        Note that instance.__init__(*args, **kwargs) gets automatically called by the python constructor
        """
        instance = object.__new__(cls)
        for member_name in dir(cls):
            member = getattr(cls, member_name, None)
            if isinstance(member, Vertex):
                setattr(instance, member_name, GraphVertex(instance, member.func))
        return instance

class DiddleScope(GraphState):
    """
    A DiddleScope object is used in conjunction with a "with" block. DiddleScopes can be nested and revert the so called "diddles" that are applied within 
    them upon exit. A "set_value" that is called within a diddle scope will remain applied until it is explicitly cleared.
    """

    def __init__(self, debug_mode=None):
        super(DiddleScope, self).__init__(_graph)
        self._parent_state = None
        self._debug_mode = debug_mode
        self._saved_debug_mode = None

    def __enter__(self):
        self._parent_state = self._graph.push_state(self)
        self._parent_state.copy(self)
        self._saved_debug_mode = self._parent_state._graph._debug_mode
        self._parent_state._graph._debug_mode = self._debug_mode

    def __exit__(self, extype, exvalue, tb):
        self._parent_state._graph._debug_mode = self._saved_debug_mode
        self._graph.pop_state()
        self.clear()
        self._parent_state = None
        return extype is None

class SetScope(object):
    def __init__(self, overrides):
        self._overrides = overrides
        self._to_revert = {}
        self._to_clear = set()

    def __enter__(self):
        for vertex, override in self._overrides.items():
            if vertex.is_fixed():
                self._to_revert[vertex] = vertex()
            else:
                self._to_clear.add(vertex)
            vertex.set_value(override)

    def __exit__(self, extype, exvalue, tb):
        for vertex, prev_value in self._to_revert.items():
            vertex.set_value(prev_value)
        for vertex in self._to_clear:
            vertex.clear_value()
        return extype is None


def is_fixed(vertex):
    if not isinstance(vertex, GraphVertex):
        raise Exception('Can only check if fixed on a GraphVertex')
    return vertex.is_fixed()

def set_diddle(vertex, value):
    if not isinstance(vertex, GraphVertex):
        raise Exception('Can only set diddle on a GraphVertex')
    vertex.set_diddle(value)

def clear_diddle(vertex):
    if not isinstance(vertex, GraphVertex):
        raise Exception('Can only clear diddle on a GraphVertex')
    vertex.clear_diddle()

def set_value(vertex, value):
    if not isinstance(vertex, GraphVertex):
        raise Exception('Can only set value on a GraphVertex')
    vertex.set_value(value)

def clear_value(vertex):
    if not isinstance(vertex, GraphVertex):
        raise Exception('Can only clear on a GraphVertex')
    vertex.clear_value

if __name__ == '__main__':
    class Example(GraphObject):
        @Vertex
        def length(self):
            return 5

        @Vertex
        def width(self):
            return 5

        @Vertex
        def area(self):
            return self.length() * self.width()

        @Vertex
        def height(self):
            return 5

        @Vertex
        def volume(self):
            return self.area() * self.height()

    class AnotherExample(GraphObject):
        def __init__(self, ieg) -> None:
            super(AnotherExample, self).__init__()
            self.ieg = ieg

        @Vertex
        def length(self):
            return self.ieg.length()

        @Vertex
        def width(self):
            return 9

        @Vertex
        def area(self):
            return self.length() * self.width()
        
    # Create example instances
    eg = Example()
    aeg = AnotherExample(eg)

    # Test basic functionality and ensure graph is populated
    print("Basic calculations:")
    print(f"Example length: {eg.length()}")
    print(f"Example area: {eg.area()}")
    print(f"Example volume: {eg.volume()}")
    print(f"AnotherExample area: {aeg.area()}")

    # Demonstrate graph analysis capabilities
    print("\nGraph Analysis:")
    
    # Get topological sort
    print("Topological sort:", _graph.get_topological_sort())
    
    # Check for cycles
    cycles = _graph.get_cycles()
    print("Cycles in graph:", "Yes" if cycles else "No")
    
    # Find paths between vertices
    paths = _graph.get_all_paths(eg.length, eg.volume)
    print("\nAll paths from length to volume:")
    for path in paths:
        print(" -> ".join(path))
    
    # Visualize the graph
    print("\nVisualizing the graph structure...")
    _graph.visualize()

    # Modify and show changes
    print("\nModifying graph:")
    eg.length.set_value(8)
    print(f"Updated Example length: {eg.length()}")
    print(f"Updated Example area: {eg.area()}")
    print(f"Updated AnotherExample area: {aeg.area()}")
    
    # Visualize the modified graph
    print("\nVisualizing the modified graph structure...")
    _graph.visualize()
    
    print("\nFinished")