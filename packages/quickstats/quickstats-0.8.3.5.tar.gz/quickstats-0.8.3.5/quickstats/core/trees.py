"""
A module providing a flexible tree data structure with named nodes.

This module implements a tree structure where each node has a name, optional data,
and can have multiple children. Nodes can be accessed using domain-style notation
(e.g., 'parent.child.grandchild') and support dict-like operations.

Examples
--------
>>> # Create a basic tree
>>> root = NamedTreeNode("root", data="root_data")
>>> root.add_child(NamedTreeNode("child1", "child1_data"))
>>> print(root)
root: 'root_data'
    child1: 'child1_data'

>>> # Use domain notation
>>> root.set("new_data", domain="child1")
>>> print(root.get(domain="child1"))
'new_data'

>>> # Use dictionary updates
>>> root |= {"name": "child2", "data": "child2_data", "children": {}}
>>> print(root)
root: 'root_data'
    child1: 'new_data'
    child2: 'child2_data'
"""
from __future__ import annotations

from typing import (
    Any, Optional, List, Dict, Union, Iterator, TypeVar, Generic, 
    Sequence, Mapping, ClassVar, get_args, get_origin, Type
)
from dataclasses import dataclass
import copy
import re

from .type_validation import check_type

# Type variables and aliases
T = TypeVar('T')
DomainType = Optional[str]
NodeData = TypeVar('NodeData')

class TreeError(Exception):
    """Base exception for tree-related errors."""
    pass

class InvalidNodeError(TreeError):
    """Exception raised for invalid node operations."""
    pass

class DomainError(TreeError):
    """Exception raised for invalid domain operations."""
    pass

class ValidationError(TreeError):
    """Exception raised for data validation errors."""
    pass

@dataclass
class NodeConfig:
    """Configuration for tree nodes.
    
    Parameters
    ----------
    separator : str, default='.'
        Separator used for domain paths
    allow_none_data : bool, default=True
        Whether to allow None as valid data
    validate_names : bool, default=False
        Whether to validate node names against pattern
    validate_data_type : bool, default=False
        Whether to validate data against the node's type parameter
    name_pattern : str, default=r'^[a-zA-Z][a-zA-Z0-9_]*$'
        Pattern for valid node names if validate_names is True
    """
    separator: str = '.'
    allow_none_data: bool = True
    validate_names: bool = False  # Default to False for performance
    validate_data_type: bool = False  # Default to False for performance
    name_pattern: str = r'^[a-zA-Z][a-zA-Z0-9_]*$'

class NamedTreeNode(Generic[NodeData]):
    """
    A tree node with a name, optional data, and child nodes.
    
    This class implements a flexible tree structure where each node has:
    - A unique name within its parent's scope
    - Optional data of any type
    - Zero or more child nodes
    - Support for domain-style access (e.g., 'parent.child.grandchild')
    
    Attributes
    ----------
    name : str
        The name of the node
    data : Optional[NodeData]
        The data stored in the node
    children : Dict[str, NamedTreeNode]
        Dictionary of child nodes keyed by their names
        
    Examples
    --------
    >>> # Create a basic tree
    >>> root = NamedTreeNode[str]("root", "root_data")
    >>> root.add_child(NamedTreeNode("child1", "child1_data"))
    >>> root["child2"] = "child2_data"
    
    >>> # Access data
    >>> print(root.get("child1"))
    'child1_data'
    >>> print(root["child2"])
    'child2_data'
    
    >>> # Update with dictionary
    >>> root |= {
    ...     "name": "child3",
    ...     "data": "child3_data",
    ...     "children": {}
    ... }
    """
    
    # Class-level configuration
    config: ClassVar[NodeConfig] = NodeConfig()
    
    def __init__(
        self, 
        name: str = 'root', 
        data: Optional[NodeData] = None,
        separator: Optional[str] = None
    ) -> None:
        """
        Initialize a named tree node.
        
        Parameters
        ----------
        name : str, default 'root'
            The name of the node. Must be a valid identifier.
        data : Optional[NodeData], default None
            The data to store in the node.
        separator : Optional[str], default None
            The separator to use for domain strings. If None, uses class default.
            
        Raises
        ------
        ValidationError
            If the name is invalid or data validation fails.
        """
        self._validate_name(name)
        self._name = name     
        self._data = data
        self._children = {}
        self._data_type = None
        self._data_type_inferred = False
        self._separator = separator or self.config.separator

    def _infer_data_type(self) -> None:
        """Infer the data type when needed."""
        if not self._data_type_inferred:
            if hasattr(self, "__orig_class__"):
                # Extract the type from the instantiated generic class
                type_args = get_args(self.__orig_class__)
                if type_args:
                    self._data_type = type_args[0]
                self._data_type_inferred = True   

    def _validate_name(self, name: str) -> None:
        """Validate node name."""
        
        if not isinstance(name, str):
            raise ValidationError(f"Name must be a string, got {type(name)}")
            
        if not name:
            raise ValidationError("Name cannot be empty")
            
        if self.config.validate_names:
            if not re.match(self.config.name_pattern, name):
                raise ValidationError(
                    f"Invalid name '{name}'. Must match pattern: {self.config.name_pattern}"
                )

    def _validate_data(self, data: Optional[NodeData]) -> Optional[NodeData]:
        """
        Validate node data.
        
        Parameters
        ----------
        data : Optional[NodeData]
            Data to validate
            
        Returns
        -------
        Optional[NodeData]
            Validated data
            
        Raises
        ------
        ValidationError
            If data validation fails
        """
        # Handle None data
        if data is None:
            if not self.config.allow_none_data:
                raise ValidationError("None data not allowed")
            return None

        # Perform type validation if enabled and type is known
        if self.config.validate_data_type and self.data_type is not None:
            if not check_type(data, self.data_type):
                raise ValidationError(
                    f"Data type mismatch: expected {self._data_type.__name__}, "
                    f"got {type(data).__name__}"
                )
        
        return data

    def _split_domain(self, domain: Optional[str] = None) -> List[str]:
        """Split domain string into components."""
        if not domain:
            return []
            
        if not isinstance(domain, str):
            domain = str(domain)
            
        return domain.split(self._separator)

    def _format_domain(self, *components: Optional[str]) -> str:
        """Format domain components into a domain string."""
        return self._separator.join(comp for comp in components if comp)

    def __setitem__(self, domain: str, data: NodeData) -> None:
        """
        Set data for a node at the specified domain.
        
        Parameters
        ----------
        domain : str
            The domain path to the node
        data : NodeData
            The data to set
        
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child.grandchild"] = "data"
        >>> print(root["child.grandchild"])
        'data'
        """
        try:
            self.set(data=data, domain=domain)
        except Exception as e:
            raise DomainError(f"Failed to set item at '{domain}': {str(e)}") from e

    def __getitem__(self, domain: str) -> NodeData:
        """
        Get data from a node at the specified domain.
        
        Parameters
        ----------
        domain : str
            The domain path to the node
            
        Returns
        -------
        NodeData
            The data at the specified domain
            
        Raises
        ------
        KeyError
            If the domain doesn't exist
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child"] = "data"
        >>> print(root["child"])
        'data'
        """
        node = self.traverse_domain(domain, create=False)
        if node is None:
            raise KeyError(f"Domain not found: '{domain}'")
        return node.data

    def __or__(self, other: Union[NamedTreeNode[NodeData], Dict[str, Any]]) -> NamedTreeNode[NodeData]:
        """
        Combine this node with another node or dictionary.
        
        Parameters
        ----------
        other : Union[NamedTreeNode[NodeData], Dict[str, Any]]
            The other node or dictionary to combine with
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A new node combining both trees
            
        Examples
        --------
        >>> node1 = NamedTreeNode[str]("node1", "data1")
        >>> node2 = NamedTreeNode[str]("node2", "data2")
        >>> combined = node1 | node2
        >>> print(combined.name)
        'node2'
        """
        if isinstance(other, dict):
            other = self.from_dict(other)
        elif not isinstance(other, NamedTreeNode):
            raise TypeError("Can only combine with another NamedTreeNode or dict")
            
        new_node = self.create(self._name, self._data)
        new_node.update(self)
        new_node.update(other)
        return new_node

    def __ior__(self, other: Union[NamedTreeNode[NodeData], Dict[str, Any]]) -> NamedTreeNode[NodeData]:
        """
        Update this node with another node or dictionary in-place.
        
        Parameters
        ----------
        other : Union[NamedTreeNode[NodeData], Dict[str, Any]]
            The other node or dictionary to update with
            
        Returns
        -------
        NamedTreeNode[NodeData]
            This node, updated
            
        Examples
        --------
        >>> node = NamedTreeNode[str]("node", "old_data")
        >>> node |= {"name": "node", "data": "new_data"}
        >>> print(node.data)
        'new_data'
        """
        self.update(other)
        return self

    def __ror__(self, other: Dict[str, Any]) -> NamedTreeNode[NodeData]:
        """
        Combine a dictionary with this node.
        
        Parameters
        ----------
        other : Dict[str, Any]
            The dictionary to combine with
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A new node combining both
        """
        new_node = self.from_dict(other)
        return new_node | self

    def __contains__(self, domain: str) -> bool:
        """
        Check if a domain exists in the tree.
        
        Parameters
        ----------
        domain : str
            The domain to check for
            
        Returns
        -------
        bool
            True if the domain exists
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child"] = "data"
        >>> print("child" in root)
        True
        """
        try:
            return self.traverse_domain(domain, create=False) is not None
        except DomainError:
            return False

    def __copy__(self) -> NamedTreeNode[NodeData]:
        """Create a shallow copy."""
        new_node = self.create(self._name, self._data)
        new_node._children = self._children.copy()
        return new_node

    def __deepcopy__(self, memo: Dict[int, Any]) -> NamedTreeNode[NodeData]:
        """Create a deep copy."""
        new_node = self.create(self._name, copy.deepcopy(self._data, memo))
        new_node._children = {
            name: copy.deepcopy(child, memo) 
            for name, child in self._children.items()
        }
        return new_node

    def __repr__(self, level: int = 0) -> str:
        """
        Create a string representation of the tree.
        
        Parameters
        ----------
        level : int, default 0
            The current indentation level
            
        Returns
        -------
        str
            A formatted string representation
        """
        indent = "  " * level
        result = [f"{indent}{self._name}: {repr(self._data)}"]
        
        for child in self._children.values():
            result.append(child.__repr__(level + 1))
            
        return "\n".join(result)

    def __iter__(self) -> Iterator[NamedTreeNode[NodeData]]:
        """
        Iterate over child nodes.
        
        Yields
        ------
        NamedTreeNode[NodeData]
            Each child node
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child1"] = "data1"
        >>> root["child2"] = "data2"
        >>> for child in root:
        ...     print(child.name)
        child1
        child2
        """
        return iter(self._children.values())

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any]
    ) -> NamedTreeNode[NodeData]:
        """
        Create a new tree from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing node data and children
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A new tree node
            
        Examples
        --------
        >>> data = {
        ...     "name": "root",
        ...     "data": "root_data",
        ...     "children": {
        ...         "child1": {
        ...             "name": "child1",
        ...             "data": "child1_data"
        ...         }
        ...     }
        ... }
        >>> root = NamedTreeNode[str].from_dict(data)
        """
        if not isinstance(data, dict):
            raise TypeError("Expected dictionary input")
            
        name = data.get('name', 'root')
        node_data = data.get('data')
        node = cls(name, node_data)
        
        children = data.get('children', {})
        if not isinstance(children, dict):
            raise TypeError("Children must be a dictionary")
            
        for child_name, child_data in children.items():
            node.add_child(cls.from_dict(child_data))
            
        return node

    @classmethod
    def from_mapping(
        cls,
        data: Mapping[str, NodeData]
    ) -> NamedTreeNode[NodeData]:
        """
        Create a new tree from a mapping.
        
        Parameters
        ----------
        data : Mapping[str, NodeData]
            Mapping containing node data
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A new tree node
            
        Examples
        --------
        >>> data = {
        ...     None: "root_data",
        ...     "child1": "child1_data",
        ...     "child2": "child2_data"
        ... }
        >>> root = NamedTreeNode[str].from_mapping(data)
        """
        node = cls()
        node.set(data.get(None))
        
        for name, value in data.items():
            if name is not None:
                node[name] = value
                
        return node

    @classmethod
    def create(
        cls,
        name: str,
        data: Optional[NodeData] = None
    ) -> NamedTreeNode[NodeData]:
        """
        Create a new tree node.
        
        Parameters
        ----------
        name : str
            Name for the node
        data : Optional[NodeData]
            Data for the node
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A new tree node
        """
        return cls(name, data)

    @property
    def name(self) -> str:
        """Get the node's name."""
        return self._name

    @property
    def data(self) -> Optional[NodeData]:
        """Get the node's data."""
        return self._data

    @property
    def data_type(self) -> Optional[Type[NodeData]]:
        """Access the inferred data type."""
        self._infer_data_type()
        return self._data_type

    @property
    def namespaces(self) -> List[str]:
        """
        Get list of immediate child names.
        
        Returns
        -------
        List[str]
            List of child names
        """
        return list(self._children.keys())

    @property
    def domains(self) -> List[str]:
        """
        Get list of all domain paths in the tree.
        
        Returns
        -------
        List[str]
            List of domain paths
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["a.b"] = "data1"
        >>> root["a.c"] = "data2"
        >>> print(root.domains)
        ['a.b', 'a.c']
        """
        result = []
        for namespace, node in self._children.items():
            subdomains = node.domains
            # NB: change to NOTSET
            if node._data is not None:
                result.append(namespace)
            if subdomains:
                result.extend([
                    self._format_domain(namespace, subdomain)
                    for subdomain in subdomains
                ])
        return result

    def format(self, *components: Optional[str]) -> str:
        """Format domain components into a domain string."""
        return self._format_domain(*components)

    def copy(self, deep: bool = False) -> NamedTreeNode[NodeData]:
        """
        Create a copy of the tree.
        
        Parameters
        ----------
        deep : bool, default False
            If True, creates a deep copy
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A copy of the tree
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root", "data")
        >>> root["child"] = "child_data"
        >>> copy1 = root.copy()  # Shallow copy
        >>> copy2 = root.copy(deep=True)  # Deep copy
        """
        return self.__deepcopy__({}) if deep else self.__copy__()

    def add_child(self, child_node: NamedTreeNode[NodeData]) -> None:
        """
        Add a child node to the tree.
        
        Parameters
        ----------
        child_node : NamedTreeNode[NodeData]
            The child node to add
            
        Raises
        ------
        TypeError
            If child_node is not a NamedTreeNode
        ValidationError
            If child node validation fails
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> child = NamedTreeNode("child", "data")
        >>> root.add_child(child)
        """
        if not isinstance(child_node, NamedTreeNode):
            raise TypeError("Child must be a NamedTreeNode instance")
            
        self._validate_child(child_node)
        self._children[child_node.name] = child_node

    def _validate_child(self, child: NamedTreeNode[NodeData]) -> None:
        """Validate a child node before adding."""
        if child.name in self._children:
            raise ValidationError(f"Child name '{child.name}' already exists")

    def get_child(
        self, 
        name: str, 
        default: Optional[NamedTreeNode[NodeData]] = None
    ) -> Optional[NamedTreeNode[NodeData]]:
        """
        Get a child node by name.
        
        Parameters
        ----------
        name : str
            Name of the child node
        default : Optional[NamedTreeNode[NodeData]], default None
            Value to return if child doesn't exist
            
        Returns
        -------
        Optional[NamedTreeNode[NodeData]]
            The child node or default value
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child"] = "data"
        >>> child = root.get_child("child")
        >>> print(child.data)
        'data'
        """
        return self._children.get(name, default)

    def remove_child(self, name: str) -> Optional[NamedTreeNode[NodeData]]:
        """
        Remove and return a child node.
        
        Parameters
        ----------
        name : str
            Name of the child to remove
            
        Returns
        -------
        Optional[NamedTreeNode[NodeData]]
            The removed child node, or None if not found
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child"] = "data"
        >>> removed = root.remove_child("child")
        >>> print(removed.data)
        'data'
        """
        return self._children.pop(name, None)

    def traverse(
        self, 
        *namespaces: str,
        create: bool = False
    ) -> Optional[NamedTreeNode[NodeData]]:
        """
        Traverse the tree through multiple namespaces.
        
        Parameters
        ----------
        *namespaces : str
            Sequence of namespace names to traverse
        create : bool, default False
            Whether to create missing nodes during traversal
            
        Returns
        -------
        Optional[NamedTreeNode[NodeData]]
            The final node or None if not found
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> node = root.traverse("a", "b", "c", create=True)
        >>> node.data = "data"
        >>> print(root["a.b.c"])
        'data'
        """
        node = self
        for namespace in namespaces:
            if not namespace:
                continue
                
            subnode = node._children.get(namespace)
            if subnode is None:
                if create:
                    subnode = self.create(namespace)
                    node.add_child(subnode)
                else:
                    return None
            node = subnode
        return node

    def traverse_domain(
        self, 
        domain: Optional[str] = None,
        create: bool = False
    ) -> Optional[NamedTreeNode[NodeData]]:
        """
        Traverse the tree using a domain string.
        
        Parameters
        ----------
        domain : Optional[str]
            Domain path (e.g., "parent.child.grandchild")
        create : bool, default False
            Whether to create missing nodes during traversal
            
        Returns
        -------
        Optional[NamedTreeNode[NodeData]]
            The final node or None if not found
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> node = root.traverse_domain("a.b.c", create=True)
        >>> node.data = "data"
        >>> print(root.get("a.b.c"))
        'data'
        """
        components = self._split_domain(domain)
        return self.traverse(*components, create=create)

    def get(
        self,
        domain: Optional[str] = None,
        default: Any = None,
        strict: bool = False
    ) -> Optional[NodeData]:
        """
        Get data from a node at the specified domain.
        
        Parameters
        ----------
        domain : Optional[str]
            Domain path to the node
        default : Any, default None
            Value to return if node not found
        strict : bool, default False
            If True, raises KeyError for missing nodes
            
        Returns
        -------
        Optional[NodeData]
            The node's data or default value
            
        Raises
        ------
        KeyError
            If strict=True and node not found
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["a.b"] = "data"
        >>> print(root.get("a.b"))
        'data'
        >>> print(root.get("x.y", default="not found"))
        'not found'
        """
        node = self.traverse_domain(domain)
        if strict and node is None:
            raise KeyError(f"Domain not found: '{domain}'")
        return node.data if node is not None else default

    def set(
        self,
        data: NodeData,
        domain: Optional[str] = None
    ) -> None:
        """
        Set data for a node at the specified domain.
        
        Parameters
        ----------
        data : NodeData
            The data to set
        domain : Optional[str]
            Domain path to the node
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root.set("data", "a.b.c")
        >>> print(root.get("a.b.c"))
        'data'
        """
        node = self.traverse_domain(domain, create=True)
        if node:
            node._data = self._validate_data(data)

    def update(
        self,
        other: Union[NamedTreeNode[NodeData], Dict[str, Any]]
    ) -> None:
        """
        Update the tree with another tree or dictionary.
        
        Parameters
        ----------
        other : Union[NamedTreeNode[NodeData], Dict[str, Any]]
            The source to update from
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root.update({
        ...     "name": "root",
        ...     "data": "new_data",
        ...     "children": {
        ...         "child": {"name": "child", "data": "child_data"}
        ...     }
        ... })
        """
        if isinstance(other, dict):
            other = self.from_dict(other)
        elif not isinstance(other, NamedTreeNode):
            raise TypeError(
                "Expected NamedTreeNode or dict, "
                f"got {type(other).__name__}"
            )

        # Update name and data
        self._name = other.name
        self._data = self._validate_data(other.data)

        # Update children
        for name, child in other._children.items():
            if name in self._children:
                self._children[name].update(child)
            else:
                self._children[name] = child

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tree to a dictionary representation.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the tree
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root", "data")
        >>> root["child"] = "child_data"
        >>> dict_repr = root.to_dict()
        >>> print(dict_repr['children']['child']['data'])
        'child_data'
        """
        return {
            "name": self._name,
            "data": self._data,
            "children": {
                name: child.to_dict()
                for name, child in self._children.items()
            }
        }

    def clear(self) -> None:
        """
        Remove all children from the tree.
        
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["a"] = "data1"
        >>> root["b"] = "data2"
        >>> root.clear()
        >>> print(len(root.children))
        0
        """
        self._children.clear()

    def merge(
        self,
        other: NamedTreeNode[NodeData],
        strategy: str = 'replace'
    ) -> None:
        """
        Merge another tree into this one.
        
        Parameters
        ----------
        other : NamedTreeNode[NodeData]
            The tree to merge from
        strategy : str, default 'replace'
            Merge strategy ('replace' or 'keep')
            
        Examples
        --------
        >>> tree1 = NamedTreeNode[str]("root")
        >>> tree1["a"] = "data1"
        >>> tree2 = NamedTreeNode[str]("root")
        >>> tree2["b"] = "data2"
        >>> tree1.merge(tree2)
        """
        if not isinstance(other, NamedTreeNode):
            raise TypeError("Can only merge with another NamedTreeNode")
            
        if strategy not in {'replace', 'keep'}:
            raise ValueError(
                "Invalid merge strategy. Must be 'replace' or 'keep'"
            )
            
        # Merge data if needed
        if strategy == 'replace' or self._data is None:
            self._data = self._validate_data(other.data)
            
        # Merge children
        for name, other_child in other._children.items():
            if name in self._children:
                self._children[name].merge(other_child, strategy)
            else:
                self._children[name] = other_child.copy(deep=True)