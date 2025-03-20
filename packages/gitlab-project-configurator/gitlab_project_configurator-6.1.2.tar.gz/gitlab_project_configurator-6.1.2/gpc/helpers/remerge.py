# Standard Library
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

# Third Party Libraries
from boltons.iterutils import default_enter
from boltons.iterutils import get_path
from boltons.iterutils import remap
from structlog import get_logger


log = get_logger()

__all__ = [
    "ListOverrideBehavior",
    "remerge",
    "sourced_remerge",
]

Container = Dict[Any, Any]
ContainerName = str
PathInContainer = Sequence

SourceMap = Dict[PathInContainer, ContainerName]
NamedContainer = Tuple[ContainerName, Container]
ContainersList = List[NamedContainer]
SourcedRemergedContainer = Tuple[Optional[Container], SourceMap]


class ListOverrideBehavior(Enum):
    """
    Behavior on list override.

    * ``REPLACE``: replace the full content of the list by override
    * ``APPEND``: append the content of the list. ``None`` in override will
      replace the list by ``None``.
      ``[]`` (empty list) in override will do nothing.
    * ``APPEND_WITH_EMPTY_MEANS_RESET``: append the content of the list.
      ``None`` in override will replace the content by None,
      ``[]`` (empty list) will clear the list.
    """

    REPLACE = "replace"
    APPEND = "append"
    APPEND_WITH_EMPTY_MEANS_RESET = "append_with_empty_means_reset"


def sourced_remerge(  # noqa: C901 (too complex)
    target_list: List[NamedContainer],
    list_update_behavior: ListOverrideBehavior = ListOverrideBehavior.REPLACE,
) -> SourcedRemergedContainer:  # noqa: D210
    """
    Merge a list of dicts (sourced version).

    Takes a list of containers (e.g., dicts) and merges them using
    boltons.iterutils.remap. Containers later in the list take
    precedence (last-wins).

    By default (``list_update_behavior=ListOverrideBehavior.REPLACE``),
    items with the "list" type are replaced with overrides.

    Setting ``list_update_behavior=ListOverrideBehavior.APPEND`` means
    lists content from override are appended to the previous content.

    Setting ``list_update_behavior=ListOverrideBehavior.APPEND_WITH_EMPTY_MEANS_RESET``
    means lists content are appended, but empty list clears the content of the
    list.

    This is the *sourced* version of ``remerge``, it expects a list of
    ``(name, container)`` pairs, and will return a pair
    ``(merged_dict, source map)``.

    The source map is a dictionary mapping between path and the name of the
    container it came from.

    Example:

    .. code-block:: python

        >>> defaults = {
        >>>     'key_to_override': 'value_from_defaults',
        >>>     'integer_to_override': 1111,
        >>>     'list_to_replace': [{
        >>>         'a': 1
        >>>     }],
        >>>     'subdict': {
        >>>         'other_subdict': {
        >>>             'key_to_override': 'value_from_defaults',
        >>>             'integer_to_override': 2222
        >>>         },
        >>>         'second_subdict': {
        >>>             'key_to_override': 'value_from_defaults',
        >>>             'integer_to_override': 3333
        >>>         }
        >>>     }
        >>> }

        >>>    first_override = {
        >>>        'key_to_override': 'value_from_first_override',
        >>>        'integer_to_override': 4444,
        >>>        'list_to_replace': [{
        >>>            'b': 2
        >>>        }],
        >>>        'subdict': {
        >>>            'other_subdict': {
        >>>                'key_to_override': 'value_from_first_override',
        >>>                'integer_to_override': 5555
        >>>            }
        >>>        },
        >>>        'added_in_first_override': 'some_string'
        >>>    }

        >>>    second_override = {
        >>>        'subdict': {
        >>>            'second_subdict': {
        >>>                'key_to_override': 'value_from_second_override'
        >>>            }
        >>>        }
        >>>    }

        >>> merged, source_map = sourced_remerge(
                [('defaults', defaults),
                ('first_override', first_override),
                ('second_override', second_override),
            ])
        >>> pprint(merged)
        >>> {
        >>>     'added_in_first_override': 'some_string',
        >>>     'integer_to_override': 4444,
        >>>     'key_to_override': 'value_from_first_override',
        >>>     'list_to_replace': [{'b': 2}],
        >>>     'subdict': {
        >>>         'other_subdict': {
        >>>             'integer_to_override': 5555,
        >>>             'key_to_override': 'value_from_first_override'
        >>>         },
        >>>         'second_subdict': {
        >>>             'integer_to_override': 3333,
        >>>             'key_to_override': 'value_from_second_override'
        >>>         }
        >>>     }
        >>> }

        >>> pprint(source_map)
        >>> {
        >>>     ('added_in_first_override',): 'first_override',
        >>>     ('integer_to_override',): 'first_override',
        >>>     ('key_to_override',): 'first_override',
        >>>     ('list_to_replace',): 'first_override',
        >>>     ('subdict',): 'second_override',
        >>>     ('subdict', 'other_subdict'): 'first_override',
        >>>     ('subdict',
                 'other_subdict', 'integer_to_override'): 'first_override',
        >>>     ('subdict',
                 'other_subdict', 'key_to_override'): 'first_override',
        >>>     ('subdict', 'second_subdict'): 'second_override',
        >>>     ('subdict',
                 'second_subdict', 'integer_to_override'): 'defaults',
        >>>     ('subdict',
                 'second_subdict', 'key_to_override'): 'second_override'
        >>> }
    """
    # Discusson in :
    # https://gist.github.com/mahmoud/db02d16ac89fa401b968
    # Final gist in:
    # https://gist.github.com/pleasantone/c99671172d95c3c18ed90dc5435ddd57

    ret = None  # type: Optional[Container]
    source_map = {}  # type: SourceMap

    def remerge_enter(path, key, value):
        new_parent, new_items = default_enter(path, key, value)
        if ret and not path and key is None:
            new_parent = ret
        try:
            cur_val = get_path(ret, path + (key,))
        except KeyError:
            pass
        else:
            # TODO: type check?
            new_parent = cur_val

        if isinstance(value, list):
            if list_update_behavior == ListOverrideBehavior.REPLACE:
                new_parent = value
            elif list_update_behavior == ListOverrideBehavior.APPEND_WITH_EMPTY_MEANS_RESET:
                if value == []:
                    new_parent.clear()
                else:
                    new_parent.extend(value)
            else:  # if list_update_behavior == ListOverrideBehavior.APPEND
                new_parent.extend(value)
            new_items = []

        return new_parent, new_items

    for t_name, target in target_list:

        def remerge_visit(path, key, _value):
            source_map[path + (key,)] = t_name  # pylint: disable=cell-var-from-loop
            return True

        ret = remap(target, enter=remerge_enter, visit=remerge_visit)

    return ret, source_map


def remerge(
    target_list: List[Container],
    list_update_behavior: ListOverrideBehavior = ListOverrideBehavior.REPLACE,
) -> Optional[Container]:  # noqa: D210
    """Merge a list of dicts (unsourced version).

    Takes a list of containers (e.g., dicts) and merges them using
    boltons.iterutils.remap. Containers later in the list take
    precedence (last-wins).

    By default (``list_update_behavior=True``), items with the "list" type are not
    replaced but items are appended. Setting ``list_update_behavior=False`` means
    lists content are replaced when overriden.

    By default, returns a new, merged top-level container.

    Example:

    .. code-block:: python

        >>> merged = remerge([defaults, first_override, second_override])
    """
    ret, _source_map = sourced_remerge(
        [(str(id(t)), t) for t in target_list],
        list_update_behavior=list_update_behavior,
    )
    return ret
