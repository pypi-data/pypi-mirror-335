import copy

from docutils import nodes

from sphinx.util.docutils import SphinxDirective

from sphinx.locale import __
from sphinx.util import logging

from sphinx_ifelse.utils import directive2location, remove_all_childs_of_types

logger = logging.getLogger(__name__)


class IfNode(nodes.General, nodes.Element):
    def __init__(self,
                 condition:str = '',
                 evaluatedto:bool = False,
                 location = None):
        self.condition = condition
        self.evaluatedto = evaluatedto
        self.location = location
        super().__init__()


class ElIfNode(nodes.General, nodes.Element):
    def __init__(self,
                 condition:str = '',
                 evaluatedto:bool = False,
                 previously_evaluatedtoTrue:bool = False,
                 location = None):
        self.condition = condition
        self.evaluatedto = evaluatedto
        self.previously_evaluatedtoTrue = previously_evaluatedtoTrue
        self.location = location
        super().__init__()


class ElseNode(nodes.General, nodes.Element):
    def __init__(self,
                 previously_evaluatedtoTrue:bool = False,
                 location = None):
        self.previously_evaluatedtoTrue = previously_evaluatedtoTrue
        self.location = location
        super().__init__()


def process_ifelse_nodes(app, doctree, fromdocname):
    nodetypes = [IfNode, ElIfNode, ElseNode]
    remove_all_childs_of_types(doctree, nodetypes)
    return

class AbstractIfEelseDirective(SphinxDirective):
    """Abstract class for common if/else logic.
    """

    def evaluate_condition(self, condition:str, name_of_directive: str)->bool:
        """
        Evaluates a given condition for a specific directive.

        Args:
            condition (str): The condition to evaluate.
            name_of_directive (str): The name of the directive associated with the condition.

        Returns:
            bool: The result of the condition evaluation.
        """

        env = self.state.document.settings.env
        variants = {}

        try:
            proceed = eval(condition, globals=variants)
        except Exception as err:
            logger.warning(
                __('exception while evaluating if directive expression: %s'),
                err,
                location=directive2location(self)
            )
            proceed = False

        return True

class IfDirective(SphinxDirective):
    """Directive to switch between alternative content in the documentation.
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True

    def run(self):
        parent = self.state.parent
        env = self.state.document.settings.env
        app = env.app

        exception_by_unresolvable_condition = app.config.ifelse_warning_by_unresolvable_condition
        variants = app.config.ifelse_variants

        if self.arguments:

            condition = self.arguments[0]

            try:
                # eval will change the globals variable, we have to avoid this,
                # so we create a deep copy
                variants_deep_copy = copy.deepcopy(variants)
                proceed = eval(condition, globals=variants_deep_copy)
            except Exception as err:
                logger.warning(
                    __('exception while evaluating if directive expression: %s'),
                    err,
                    location=directive2location(self)
                )
                proceed = False

        else:
            logger.warning(
                'if directive with empty condition. Handled as it was set to True.',
                location=directive2location(self)
            )
            proceed = True
            condition = ''

        selfnode = IfNode(
            condition=condition,
            evaluatedto=proceed,
            location=directive2location(self)
        )

        if not proceed:
            return [selfnode]

        parsed = self.parse_content_to_nodes(allow_section_headings=True)
        parsed.append(selfnode)
        return parsed


class ElIfDirective(SphinxDirective):
    """Directive to switch between alternative content in the documentation.
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True

    def run(self):
        parent = self.state.parent
        env = self.state.document.settings.env
        app = env.app

        exception_by_unresolvable_condition = app.config.ifelse_warning_by_unresolvable_condition
        variants = app.config.ifelse_variants

        if self.arguments:

            condition = self.arguments[0]

            try:
                # eval will change the globals variable, we have to avoid this,
                # so we create a deep copy
                variants_deep_copy = copy.deepcopy(variants)
                proceed = eval(condition, globals=variants_deep_copy)
            except Exception as err:
                logger.warning(
                    __('exception while evaluating elif directive expression: %s'),
                    err,
                    location=directive2location(self)
                )
                proceed = False

        else:
            logger.warning(
                'elif directive with empty condition. Handled as it was set to True.',
                location=directive2location(self)
            )
            condition = ''
            proceed = True

        previously_evaluatedtoTrue:bool = False
        last_sibling = parent[-1]

        if isinstance(last_sibling, IfNode):
            previously_evaluatedtoTrue = last_sibling.evaluatedto
        elif isinstance(last_sibling, ElIfNode):
            previously_evaluatedtoTrue = (last_sibling.evaluatedto or last_sibling.previously_evaluatedtoTrue)
        else:
            logger.warning(
                'elif directive without a preceding if or elif directive. '+ \
                'You may have missed to add if or elif directive, or there is a miss-intendition.',
                location=directive2location(self)
            )
            previously_evaluatedtoTrue = False

        selfnode = ElIfNode(
            condition=condition,
            evaluatedto=proceed,
            previously_evaluatedtoTrue = previously_evaluatedtoTrue,
            location=directive2location(self)
        )

        if not proceed or previously_evaluatedtoTrue:
            return [selfnode]

        parsed = self.parse_content_to_nodes(allow_section_headings=True)
        parsed.append(selfnode)
        return parsed


class ElseDirective(SphinxDirective):
    """Directive to switch between alternative content in the documentation.
    """

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    has_content = True

    def run(self):
        parent = self.state.parent
        env = self.state.document.settings.env
        app = env.app

        variants = env.config.ifelse_variants

        previously_evaluatedtoTrue:bool = False
        last_sibling = parent[-1]

        if isinstance(last_sibling, IfNode):
            previously_evaluatedtoTrue = last_sibling.evaluatedto
        elif isinstance(last_sibling, ElIfNode):
            previously_evaluatedtoTrue = (last_sibling.evaluatedto or last_sibling.previously_evaluatedtoTrue)
        else:
            logger.warning(
                'else directive without a preceding if or elif directive. '+ \
                'You may have missed to add if or elif directive, or there is a miss-intendition.',
                location=directive2location(self)
            )
            previously_evaluatedtoTrue = False

        selfnode = ElseNode(
            previously_evaluatedtoTrue = previously_evaluatedtoTrue,
            location=directive2location(self)
        )

        if previously_evaluatedtoTrue:
            return [selfnode]

        parsed = self.parse_content_to_nodes(allow_section_headings=True)
        parsed.append(selfnode)
        return parsed
