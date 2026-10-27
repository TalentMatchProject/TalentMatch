
from rest_framework import viewsets

from .models import Offer
from .serializers import OfferSerializer
from .permissions import IsRecruiterOrReadOnly


class OfferViewSet(viewsets.ModelViewSet):
    """
    API para consultar y gestionar ofertas de trabajo.
    """

    queryset = Offer.objects.all().prefetch_related(
        "offer_skills",
        "organization",
    )
    serializer_class = OfferSerializer
    permission_classes = [IsRecruiterOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Los recruiters pueden gestionar ofertas, incluidas las borrador.
        if user.is_authenticated and (
            user.is_staff
            or user.role == user.Role.RECRUITER
        ):
            return queryset

        # El resto solo puede consultar ofertas publicadas.
        return queryset.filter(status="publicada")
