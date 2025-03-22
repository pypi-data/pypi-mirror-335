ArtD Module
=============
ArtD Module is a package that is responsible for keeping track of the installed packages
-----------------------------------------------------------------------------------------
1. Add "artd_modules" to your INSTALLED_APPS setting like this:

.. code-block:: python

    INSTALLED_APPS = [
        'artd_modules',
    ]


2. Run the migration commands:
   
.. code-block::
    
        python manage.py makemigrations
        python manage.py migrate