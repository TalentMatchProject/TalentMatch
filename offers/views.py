from rest_framework import viewsets, permissions
from .models import Offer
from .serializers import OfferSerializer

class OfferViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite visualizar, crear y editar ofertas de trabajo.
    """
    queryset = Offer.objects.all().prefetch_related('offer_skills', 'organization')
    serializer_class = OfferSerializer
    
    # PERMISOS: Cualquiera puede ver las ofertas, pero solo usuarios autenticados pueden crear/editar
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # FILTROS: Filtra el catálogo para que en producción solo se vean las ofertas publicadas
    def get_queryset(self):
        queryset = super().get_queryset()
        # Si el usuario no es administrador y busca ofertas, solo le mostramos las 'publicadas'
        if not self.request.user.is_staff:
            return queryset.filter(status='publicada')
        return queryset

