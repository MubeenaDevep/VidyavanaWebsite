import django_filters

from .models import Course


class CourseFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__slug", lookup_expr="iexact")
    level = django_filters.CharFilter(field_name="level", lookup_expr="iexact")
    min_fee = django_filters.NumberFilter(field_name="fee", lookup_expr="gte")
    max_fee = django_filters.NumberFilter(field_name="fee", lookup_expr="lte")
    featured = django_filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = Course
        fields = ["category", "level", "min_fee", "max_fee", "featured", "certificate_included"]
