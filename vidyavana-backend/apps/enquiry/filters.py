import django_filters

from .models import Enquiry


class EnquiryFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    source = django_filters.CharFilter(field_name="source", lookup_expr="iexact")
    course = django_filters.CharFilter(field_name="course__slug", lookup_expr="iexact")
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Enquiry
        fields = ["status", "source", "course", "created_after", "created_before"]
