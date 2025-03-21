"""

"""
from pyforged.commons.patterns.undefined import DotDict
from pyforged.namespaces import NamespaceManager
from pyforged.ecosystem.bases import PyForgeProjectRegistry
from pyforged.__bases__ import BaseForgeProject

#

native_registry = PyForgeProjectRegistry().registry

FORGED = NamespaceManager()

#
for project, meta in native_registry.items():
    metadata = DotDict().from_dict(meta)
    FORGED.set(f"pyforged.ecosystem.{project}", metadata)

print(FORGED.list_all_namespaces())

#

FORGED.set("pyforged.build", {})

PYFORGED = FORGED.get("pyforged")
print(PYFORGED)
print(PYFORGED["ecosystem"])

APP = NamespaceManager()
print(FORGED.list_all_namespaces())