# contrib
from elasticsearch_dsl.query import Q

# app
from ..documents import FeatureFlag

# typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_elasticsearch_dsl.search import Search


def search(
    term: str,
    start: int,
    end: int,
) -> "Search":

    # Trigram
    query = Q(
        "match",
        title__trigram=term,
    )

    return (
        FeatureFlag
        .search()
        .query(query)[start: end]
    )
