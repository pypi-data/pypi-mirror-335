import hou
import os

def get_plugin_definitions():
    """Get HDA definitions that are not built-in."""
    result = []
    for category in hou.nodeTypeCategories().values():
        for node_type in category.nodeTypes().values():
            if node_type.instances():
                definition = node_type.definition()
                if definition:
                    path = definition.libraryFilePath()
                    if path and not path.startswith(os.environ["HFS"]):
                        result.append(definition)
    return result