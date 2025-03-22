ArtD Location
=============
ArtD location is a package that makes it possible to have countries, regions and cities with their respective coding, by default we have all the regions and cities of Colombia.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1. Add "artd_location" to your INSTALLED_APPS setting like this:

.. code-block:: python

    INSTALLED_APPS = [
        'artd_location',
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