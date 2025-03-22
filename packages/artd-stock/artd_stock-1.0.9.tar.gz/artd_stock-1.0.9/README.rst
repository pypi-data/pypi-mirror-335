ArtD Stock
==========
Art Product is a package that makes it possible to manage stock and stock changes.
----------------------------------------------------------------------------------
1. Add to your INSTALLED_APPS setting like this:

.. code-block:: python

    INSTALLED_APPS = [
        'django-json-widget'
        'artd_location',
        'artd_partner',
        'artd_product',
        'artd_stock',
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
        python manage.py create_taxes