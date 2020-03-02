import django_filters
from GED.models import Document

class ProductFilter(django_filters.FilterSet):
    titre_fichier = django_filters.CharFilter()
    matiere = django_filters.CharFilter(field_name='matiere', lookup_expr='icontains')

    date_publication = django_filters.NumberFilter(field_name='upload_date', lookup_expr='year')
    date_publication__gt = django_filters.NumberFilter(field_name='upload_date', lookup_expr='year__gt')
    date_publication__lt = django_filters.NumberFilter(field_name='upload_date', lookup_expr='year__lt')
    note_gt = django_filters.NumberFilter(field_name='note', lookup_expr='note_count')
    filiere = django_filters.CharFilter(field_name='filiere', lookup_expr='icontains')

    class Meta:
        model = Document