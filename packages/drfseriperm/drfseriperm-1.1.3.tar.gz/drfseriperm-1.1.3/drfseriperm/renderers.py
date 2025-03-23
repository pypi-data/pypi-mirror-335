import typing

import rest_framework.renderers


class BrowsableAPINoFieldsRenderer(
    rest_framework.renderers.BrowsableAPIRenderer,
):
    """
    Extension for drf BrowsableAPIRenderer,
    which removes http method from a page instead of
    raising for all the page in case if there are no fields
    to serialize
    """

    @staticmethod
    def _suppress_no_fields_exception(fn: typing.Callable) -> typing.Callable:

        def __wrapper__(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                # if exception was raised because of
                # there is no fields to serialize, then
                # we just return None
                if getattr(exc, '_no_fields_exception', False):
                    return
                # in other case raise exception as usual
                raise exc

        return __wrapper__

    def __getattribute__(self, item: str) -> typing.Any:
        attr = super().__getattribute__(item)

        if not callable(attr):
            return attr

        # preventing recursion while infinitely wrapping our callable
        if item == '_suppress_no_fields_exception':
            return attr

        return self._suppress_no_fields_exception(attr)
