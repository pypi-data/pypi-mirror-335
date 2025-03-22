ArtD Customer
=============
Art Customer is a package that makes it possible to manage customers, tags, addresses and additional fields.
------------------------------------------------------------------------------------------------------------
1. Add to your INSTALLED_APPS setting like this:

.. code-block:: python
    
    INSTALLED_APPS = [
        'artd_modules',
        'artd_service',
        'artd_location',
        'artd_partner',
        'django-json-widget'
        'artd_customer'
    ]

2. Run the migration commands:
   
.. code-block::
    
        python manage.py makemigrations
        python manage.py migrate

3. Run the seeder data:
   
.. code-block::
    
        python manage.py create_countries
        python manage.py create_colombian_regions
        python manage.py create_colombian_cities
        python manage.py create_base_customer_groups
        python manage.py create_tax_segments
        python manage.py create_vat_data