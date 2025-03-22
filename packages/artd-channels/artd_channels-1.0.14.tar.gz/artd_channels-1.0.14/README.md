# ArtD Channels

The ArtD Channels package allows integration with SMS and Whatsapp channels through various providers such as AWS, Messagebird and others.

## How to use?

1. Install The package
```bash
pip install artd-channels
```

2. Add the required on settings.py as follows
```python
INSTALLED_APPS = [
    "artd-customer",
    "artd-location",
    "artd-modules",
    "artd-partner",
    "artd-service",
    'artd_channels',
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
python manage.py create_services
python manage.py create_base_customer_groups
python manage.py create_tax_segments
python manage.py create_vat_data
python manage.py populate_channels
python manage.py populate_providers
```

5. Create a superuser
```bash
python manage.py createsuperuser
```

6. Log in to your Django instance manager
