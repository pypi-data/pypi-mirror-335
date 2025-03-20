# python
import logging

# contrib
from django_elasticsearch_dsl.search import Search
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

# sparkplug
from sparkplug_core.views import SearchView

# app
from .. import (
    models,
    permissions,
    serializers,
)
from ..search import (
    autocomplete,
    search,
)


log = logging.getLogger(__name__)


class AdminSearch(
    SearchView,
):
    model = models.FeatureFlag

    serializer_class = serializers.FeatureFlagTeaser

    permission_classes = (permissions.Admin,)

    def get_search_query(self, **kwargs) -> Search:
        term = kwargs.get("term", "")
        start = kwargs.get("start", 1)
        end = kwargs.get("end", 1)
        return search(term, start, end)

    @action(
        detail=False,
        methods=["get"],
    )
    def autocomplete(self, request: Request) -> Response:
        term = request.query_params.get("term", "")

        search_query = autocomplete(term)
        self.log_scores(search_query)

        response = search_query.execute()

        serializer = self.get_serializer(response, many=True)

        return Response(
            status=status.HTTP_200_OK,
            data=serializer.data,
        )
