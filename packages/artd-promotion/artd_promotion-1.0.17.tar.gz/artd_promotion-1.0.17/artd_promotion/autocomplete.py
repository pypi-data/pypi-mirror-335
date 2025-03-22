from dal import autocomplete
from django.utils.html import escape
from artd_product.models import Product, GroupedProduct


class ProductAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Product.objects.none()

        grouped_qs = GroupedProduct.objects.all()
        product_ids = []
        if self.q:
            grouped_qs = grouped_qs.filter(name__icontains=self.q)
            for item in grouped_qs:
                products = item.products.all()
                for product in products:
                    product_ids.append(product.id)

        if len(product_ids) == 0:
            qs = Product.objects.none()
        else:
            qs = Product.objects.filter(id__in=product_ids)

        return qs

    def get_result_label(self, result):
        return escape(result)

    def get_selected_result_label(self, result):
        return escape(result)
