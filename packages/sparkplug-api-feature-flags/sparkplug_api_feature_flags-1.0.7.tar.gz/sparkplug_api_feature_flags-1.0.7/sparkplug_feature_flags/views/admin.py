# python
import logging

# django
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

# contrib
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

# sparkplug
from sparkplug_core.utils import send_client_action
from sparkplug_core.views import UpdateView

# app
from .. import (
    enums,
    models,
    permissions,
)
from ..serializers import (
    FeatureFlagExpanded,
    FeatureFlagTeaser,
    FeatureFlagWrite,
    FlagAccessRead,
)


log = logging.getLogger(__name__)


class Admin(
    UpdateView,
    viewsets.ModelViewSet,
):
    model = models.FeatureFlag

    retrieve_serializer_class = FeatureFlagExpanded
    list_serializer_class = FeatureFlagTeaser
    write_serializer_class = FeatureFlagWrite

    permission_classes = (permissions.Admin,)

    def get_detail_queryset(self) -> QuerySet[models.FeatureFlag]:
        return self.model.objects.all()

    def get_list_queryset(self) -> QuerySet[models.FeatureFlag]:
        return self.model.objects.all().order_by("-created")

    def perform_update(
        self,
        serializer: FeatureFlagWrite,
    ) -> None:

        instance = serializer.save()
        target_uuids = instance.get_item_subscribers()

        send_client_action(
            target_uuids=target_uuids,
            action_type=enums.FeatureFlagAction.UPDATE,
            payload={
                "uuid": instance.uuid,
                "data": serializer.data,
            },
        )

    @action(
        detail=True,
        methods=["put"],
        url_path="add-user",
    )
    def add_user(
        self,
        request: Request,
        uuid: str,
    ) -> Response:

        instance = self.get_object()

        try:
            uuid = request.data["user_uuid"]
            user = get_user_model().objects.get(uuid=uuid)
            instance.users.add(user)

        except get_user_model().DoesNotExist:
            pass

        qs = models.FlagAccess.objects.filter(
            user=user,
            feature_flag__uuid=uuid,
        )

        serializer = FlagAccessRead(qs, many=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["put"],
        url_path="remove-user",
    )
    def remove_user(
        self,
        request: Request,
        uuid: str,
    ) -> Response:
        instance = self.get_object()

        try:
            uuid = request.data["user_uuid"]
            user = get_user_model().objects.get(uuid=uuid)
            instance.users.remove(user)

        except get_user_model().DoesNotExist:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["get"],
    )
    def teaser(
        self,
        request: Request,  # noqa: ARG002
        uuid: str,  # noqa: ARG002
    ) -> Response:
        instance = self.get_object()
        serializer = FeatureFlagTeaser(instance=instance)

        return Response(
            status=status.HTTP_200_OK,
            data=serializer.data,
        )
