"""
DSA Engine package for hospital management system.
Implements all required data structures for medical analysis.
"""

from .arrays import MedicalArray
from .linked_list import MedicalLinkedList
from .hash_map import MedicalHashMap
from .sets import MedicalSet
from .queues import MedicalQueue, PriorityQueue
from .stacks import MedicalStack
from .trees import DecisionTree, MedicalTree
from .graphs import SymptomDiseaseGraph
from .heaps import MedicalHeap, MaxHeap

__all__ = [
    'MedicalArray',
    'MedicalLinkedList',
    'MedicalHashMap',
    'MedicalSet',
    'MedicalQueue',
    'PriorityQueue',
    'MedicalStack',
    'DecisionTree',
    'MedicalTree',
    'SymptomDiseaseGraph',
    'MedicalHeap',
    'MaxHeap'
]

