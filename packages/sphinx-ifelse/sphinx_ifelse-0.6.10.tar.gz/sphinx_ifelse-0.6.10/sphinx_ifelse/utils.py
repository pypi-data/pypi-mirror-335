
from typing import Tuple
from sphinx.util.docutils import SphinxDirective

from sphinx.util.tags import Tags

def directive2location(self: SphinxDirective) -> Tuple[str, int]:
    return (self.state.document.settings.env.docname, self.lineno)

def tags2dict(tags: Tags) -> dict:
    return dict.fromkeys(tags._tags, True)

def remove_all_childs_of_types(node, nodetypes):
    to_be_removed = []
    # We have to run the list of children reversed,
    # as we change the parent during processing.
    for child in reversed(node.children):
        if len(child.children) > 0:
            remove_all_childs_of_types(child, nodetypes)
        for nodetype in nodetypes:
            if isinstance(child, nodetype):
                to_be_removed.append(child)
                node.remove(child)
                break
    return
