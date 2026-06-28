import django_filters
from .models import Job, Application


class JobFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    emirate = django_filters.CharFilter(lookup_expr='iexact')
    job_type = django_filters.CharFilter(lookup_expr='iexact')
    experience_level = django_filters.CharFilter(lookup_expr='iexact')
    is_featured = django_filters.BooleanFilter()
    is_urgent = django_filters.BooleanFilter()
    salary_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')

    class Meta:
        model = Job
        fields = ['category', 'emirate', 'job_type', 'experience_level', 'is_featured', 'is_urgent']


class ApplicationFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='iexact')
    job = django_filters.NumberFilter(field_name='job__id')
    category = django_filters.CharFilter(field_name='job__category__slug')
    emirate = django_filters.CharFilter(field_name='job__emirate')
    date_from = django_filters.DateFilter(field_name='applied_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='applied_at', lookup_expr='lte')

    class Meta:
        model = Application
        fields = ['status', 'job', 'category', 'emirate']