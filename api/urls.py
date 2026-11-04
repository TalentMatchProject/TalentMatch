from django.urls import path
from rest_framework.routers import DefaultRouter
from chat.views import ConversationViewSet
from notifications.views import NotificationViewSet

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
router.register("conversations", ConversationViewSet, basename="conversation")
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("offers/popular/", PopularOffersAPIView.as_view(), name="popular-offers"),
]

urlpatterns += router.urls