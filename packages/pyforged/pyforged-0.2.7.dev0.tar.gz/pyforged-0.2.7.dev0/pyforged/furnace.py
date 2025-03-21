"""

"""
from platform import system

from pyforged.namespacing.tree import print_namespace
from pyforged.ecosystem.bases import PyForgeProjectRegistry
from pyforged.ecosystem.forest import ForgedEcosystem
from pyforged.namespacing.core.namespace import Namespace
from pyforged.namespacing.core.decorators import register
from pyforged.services import ServiceRegistry

GLOBAL_NAMESPACES = Namespace(name='globe')

GLOBAL_NAMESPACES.register("testing.hello", 123)

print(GLOBAL_NAMESPACES.to_dict())

