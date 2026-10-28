import django_filters

from offers.models import Offer


class OfferFilter(django_filters.FilterSet):
    min_salary = django_filters.NumberFilter(
        field_name="salary_min",
        lookup_expr="gte",
    )
    max_salary = django_filters.NumberFilter(
        field_name="salary_max",
        lookup_expr="lte",
    )
    skill = django_filters.NumberFilter(
        field_name="offer_skills__skill",
        distinct=True,
    )

    class Meta:
        model = Offer
        fields = ["organization", "modality", "status"]