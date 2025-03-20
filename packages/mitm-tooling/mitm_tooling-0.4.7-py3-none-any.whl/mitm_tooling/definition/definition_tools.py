from collections.abc import Iterable
from typing import TypeVar, TypedDict, Callable, Generic

from . import MITMDefinition
from .definition_representation import ConceptName

T = TypeVar('T')


def _dummy(): return None


def _dummy_list(): return []


Mapper = Callable[[], T | tuple[str, T]]
MultiMapper = Callable[[], list[T] | Iterable[tuple[str, T]]]


class ColGroupMaps(TypedDict, Generic[T], total=False):
    kind: Mapper | None
    type: Mapper | None
    identity: MultiMapper | None
    inline: MultiMapper | None
    foreign: MultiMapper | None
    attributes: MultiMapper | None


def map_col_groups(mitm_def: MITMDefinition, concept: ConceptName, col_group_maps: ColGroupMaps[T],
                   prepended_cols: MultiMapper | None = None,
                   appended_cols: MultiMapper | None = None,
                   ensure_unique: bool = True) -> \
        tuple[
            list[T], dict[str, T]]:
    concept_properties = mitm_def.get_properties(concept)

    created_results = {}
    results = []

    def add_results(cols: Iterable[T | tuple[str, T]]):
        for item in cols:
            if isinstance(item, tuple):
                name, result = item
            else:
                result = item
                name = str(item)
            if result is not None and (not ensure_unique or name not in created_results):
                created_results[name] = result
                results.append(result)

    if prepended_cols:
        add_results(prepended_cols())
    for column_group in concept_properties.column_group_ordering:

        match column_group:
            case 'kind' if concept_properties.is_abstract or concept_properties.is_sub:
                add_results([col_group_maps.get('kind', _dummy)()])
            case 'type':
                add_results([col_group_maps.get('type', _dummy)()])
            case 'identity-relations':
                add_results(col_group_maps.get('identity', _dummy_list)())
            case 'inline-relations':
                add_results(col_group_maps.get('inline', _dummy_list)())
            case 'foreign-relations':
                add_results(col_group_maps.get('foreign', _dummy_list)())
            case 'attributes' if concept_properties.permit_attributes:
                add_results(col_group_maps.get('attributes', _dummy_list)())
    if appended_cols:
        add_results(appended_cols())

    return results, created_results
