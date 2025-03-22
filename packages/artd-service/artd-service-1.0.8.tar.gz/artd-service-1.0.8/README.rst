ArtD Service
============
ArtD Service.
--------------
1. Add to your INSTALLED_APPS setting like this:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'artd_modules',
        'artd_service',
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
        python manage.py create_apps
        python manage.py create_services
        python manage.py insert_installed_apps_and_permissions