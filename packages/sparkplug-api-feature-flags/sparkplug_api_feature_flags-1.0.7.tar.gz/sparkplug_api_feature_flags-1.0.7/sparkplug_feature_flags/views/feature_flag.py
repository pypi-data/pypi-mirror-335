# python
import logging

# django
from django.db.models import QuerySet

# contrib
from rest_framework import viewsets

# sparkplug
from sparkplug_core.views import BaseView

from .. import (
    models,
    permissions,
    serializers,
)


log = logging.getLogger(__name__)


class FeatureFlag(
    BaseView,
    viewsets.ReadOnlyModelViewSet,
):
    model = models.FeatureFlag

    retrieve_serializer_class = serializers.FeatureFlagExpanded
    list_serializer_class = serializers.FeatureFlagTeaser

    permission_classes = (permissions.FeatureFlag,)

    def get_detail_queryset(self) -> QuerySet[models.FeatureFlag]:
        return self.model.objects.all()

    def get_list_queryset(self) -> QuerySet[models.FeatureFlag]:
        return self.model.objects.all().order_by("-created")
