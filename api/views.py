from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from core.models import Skill
from offers.models import Offer, SavedOffer, StatusChoices
from organizations.models import Membership, Organization

from .filters import OfferFilter
from .permissions import IsOrganizationMemberOrReadOnly, is_member
from .serializers import (
    OfferSerializer,
    OrganizationSerializer,
    SavedOfferSerializer,
    SkillSerializer,
)


def base_offers():
    return (
        Offer.objects.select_related("organization", "created_by")
        .prefetch_related("offer_skills__skill")
        .annotate(saved_count=Count("saved_by", distinct=True))
    )


def published_offers():
    return base_offers().filter(status=StatusChoices.PUBLICADA)


class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOrganizationMemberOrReadOnly,
    ]
    filterset_class = OfferFilter
    search_fields = [
        "title",
        "description",
        "location",
        "organization__name",
        "offer_skills__skill__name",
    ]
    ordering_fields = ["salary_min", "salary_max", "created_at", "saved_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = base_offers()
        if user.is_staff:
            return queryset
        published = Q(status=StatusChoices.PUBLICADA)
        if user.is_authenticated:
            mine = Q(
                organization__in=Membership.objects.filter(user=user).values("organization")
            )
            return queryset.filter(published | mine)
        return queryset.filter(published)

    def perform_create(self, serializer):
        organization = serializer.validated_data["organization"]
        if not is_member(self.request.user, organization):
            raise PermissionDenied("No perteneces a esta organización.")
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        organization = serializer.validated_data.get("organization")
        if organization and not is_member(self.request.user, organization):
            raise PermissionDenied("No perteneces a esta organización.")
        serializer.save()

    @action(
        detail=True,
        methods=["post"],
        url_path="save",
        url_name="save",
        permission_classes=[IsAuthenticated],
    )
    def save_offer(self, request, pk=None):
        offer = self.get_object()
        if is_member(request.user, offer.organization):
            return Response(
                {"detail": "No puedes guardar ofertas de tu organización."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        saved, created = SavedOffer.objects.get_or_create(
            user=request.user,
            offer=offer,
        )
        if created:
            return Response({"saved": True}, status=status.HTTP_201_CREATED)

        saved.delete()
        return Response({"saved": False}, status=status.HTTP_200_OK)


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.filter(is_active=True).order_by("name")
    serializer_class = OrganizationSerializer


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.filter(is_active=True).order_by("name")
    serializer_class = SkillSerializer


class SavedOfferViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SavedOfferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return SavedOffer.objects.none()
        return (
            SavedOffer.objects.filter(user=self.request.user)
            .select_related("offer", "offer__organization", "offer__created_by")
            .prefetch_related("offer__offer_skills__skill")
        )


class PopularOffersAPIView(ListAPIView):
    serializer_class = OfferSerializer

    def get_queryset(self):
        return published_offers().order_by("-saved_count", "-created_at")[:20]