from sphinx_ifelse import __version__ as sphinx_ifelse_version

from typing import Any, Dict, List

from sphinx.application import Sphinx

from sphinx_ifelse.directives import IfNode, IfDirective
from sphinx_ifelse.directives import ElIfNode, ElIfDirective
from sphinx_ifelse.directives import ElseNode, ElseDirective
from sphinx_ifelse.directives import process_ifelse_nodes

def setup(app: Sphinx) -> Dict[str, Any]:
    #see https://www.sphinx-doc.org/en/master/development/tutorials/extending_build.html

    app.add_config_value(name="ifelse_warning_by_unresolvable_condition",
                         default=True,
                         rebuild="html",#"env",
                         types=bool,
                         description="Raise a warning if a condition cannot be resolved.",
                        )

    app.add_config_value(name="ifelse_variants",
                         default={'empty': True},
                         rebuild="html",
                         types=Dict[str, Any],
                         description="A dictionary of variants to be used inside the confition of a if directive.",
                        )

    app.add_node(IfNode)
    app.add_node(ElIfNode)
    app.add_node(ElseNode)

    app.add_directive("if", IfDirective)
    app.add_directive("elif", ElIfDirective)
    app.add_directive("else", ElseDirective)

    app.connect('doctree-resolved', process_ifelse_nodes)

    return {
        "version": sphinx_ifelse_version,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "env_version": None,
    }
