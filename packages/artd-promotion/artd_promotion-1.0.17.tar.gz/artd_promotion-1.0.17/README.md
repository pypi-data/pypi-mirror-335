# ArtD Promotion

Art Promotion is a package that manage coupon codes.

## How to use?

1. Install The package
```bash
pip install artd-alliance
```

2. Add the required on settings.py as follows

```python
INSTALLED_APPS = [
    "django-json-widget",
    "artd-customer",
    "artd-location",
    "artd-modules",
    "artd-partner",
    "artd-product",
    "artd-service",
    "artd-urls",
]
```

3. Run the migrations command
```bash
python manage.py migrate
```

4. Run the base commands
```bash
python manage.py create_countries
python manage.py create_colombian_regions
python manage.py create_colombian_cities
python manage.py create_apps
python manage.py create_services
python manage.py create_base_customer_groups
python manage.py create_tax_segments
python manage.py create_vat_data
python manage.py create_taxes
python manage.py insert_installed_apps_and_permissions
```