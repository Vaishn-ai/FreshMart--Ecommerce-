import django_filters as df
from .models import Product


class ProductFilter(df.FilterSet):
    min_price = df.NumberFilter(field_name="discount_price", lookup_expr="gte")
    max_price = df.NumberFilter(field_name="discount_price", lookup_expr="lte")
    category = df.CharFilter(field_name="category__slug")
    brand = df.CharFilter(field_name="brand__slug")
    min_rating = df.NumberFilter(field_name="rating_avg", lookup_expr="gte")
    in_stock = df.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["category", "brand", "is_featured", "is_flash_sale", "in_stock"]

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(stock__gt=0) if value else queryset.filter(stock=0)
