from inspect import getfullargspec
from typing import Any, Callable

from django.template.base import Parser, Token
from django.template.library import InclusionNode, parse_bits


class WorkspaceInclusionAdminNode(InclusionNode):
    """Template tag that allows its template to be overridden per model, per app, or globally."""

    def __init__(
        self, parser: Parser, token: Token, func: Callable, template_name: str, takes_context: bool = True
    ) -> None:
        self.template_name = template_name
        params, varargs, varkw, defaults, kwonly, kwonly_defaults, _ = getfullargspec(func)
        bits = token.split_contents()
        args, kwargs = parse_bits(
            parser,
            bits[1:],
            params,
            varargs,
            varkw,
            defaults,
            kwonly,
            kwonly_defaults,
            takes_context,
            bits[0],
        )
        super().__init__(func, takes_context, args, kwargs, filename=None)

    def render(self, context: dict[str, Any]) -> str:
        opts = context["opts"]
        app_label = opts.app_label.lower()
        object_name = opts.model_name
        # Load template for this render call. (Setting self.filename isn't
        # thread-safe.)
        context.render_context[self] = context.template.engine.select_template(
            [
                "workspace/%s/%s/%s" % (app_label, object_name, self.template_name),
                "workspace/%s/%s" % (app_label, self.template_name),
                "workspace/%s" % self.template_name,
            ],
        )
        return super().render(context)
