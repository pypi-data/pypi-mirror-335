# ArtD Alliance

The ArtD Alliance module allows different parties to partner to create promotional strategies such as percentage or fixed discounts and discount coupons of different types.

## How to use?

1. Install The package
```bash
pip install artd-alliance
```

2. Add the required on settings.py as follows
```python
INSTALLED_APPS = [
    "django_json_widget",
    "artd_customer",
    "artd_location",
    "artd_modules",
    "artd_partner",
    "artd_product",
    "artd_service",
    "artd_urls",
    "artd_promotion",
    "artd_alliance",
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

5. Create a superuser
```bash
python manage.py createsuperuser
```
6. Add the context processor

```bash
 TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'artd_alliance.context_processors.user_context_processor',

            ],
        }
    },
]
```

6. Log in to your Django instance manager

7. Create a partner

8. Configure your partners and alliances
