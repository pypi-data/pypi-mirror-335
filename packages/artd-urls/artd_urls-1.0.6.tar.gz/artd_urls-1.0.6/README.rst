ArtD URLS
============
Art URL is a module that is responsible for creating URLs for products
-----------------------------------------------------------------------
1. Add to your INSTALLED_APPS setting like this:

.. code-block:: python

    INSTALLED_APPS = [
        'dal',
        'dal_select2',
        'django-json-widget'
        'artd_modules',
        'artd_location',
        'artd_partner',
        'aartd_urls'
    ]

1. Run the migration commands:
   
.. code-block::
    
        python manage.py makemigrations
        python manage.py migrate

3. Run the seeder data:
   
.. code-block::

        python manage.py create_countries
        python manage.py create_colombian_regions
        python manage.py create_colombian_cities