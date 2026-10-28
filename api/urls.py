from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    OfferViewSet,
    OrganizationViewSet,
    PopularOffersAPIView,
    SavedOfferViewSet,
    SkillViewSet,
)

router = DefaultRouter()
router.register("offers", OfferViewSet, basename="offer")
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("skills", SkillViewSet, basename="skill")
router.register("saved-offers", SavedOfferViewSet, basename="saved-offer")

urlpatterns = [
    path("offers/popular/", PopularOffersAPIView.as_view(), name="popular-offers"),
]

urlpatterns += router.urls