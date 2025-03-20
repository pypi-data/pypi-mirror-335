# django-dbsettings

dbsettings is a simple reusable Django app allowing you to store key-value
pairs in your database, so you can store configuation in your database easily.

## Quick start

1. Add "dbsettings" to your INSTALLED_APPS setting like this:

   ```python
   INSTALLED_APPS = [
        ...,
        'dbsettings',
    ]
    ```

2. Run ``python manage.py makemigrations dbsettings`` and 
   ``python manage.py migrate dbsettings`` to create the models.

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to add configuration values or use dbsettings.functions.setValue(key, value)
   in your code.

4. To retrieve a configuration value from the database, use
   dbsettings.functions.getValue(key) in your code.

## Upgrade notes

When upgrading to 0.9 from a previous version, your database tables will need
to be updated. To do this, just execute step 2 from the "Quick start" section
again.

When upgrading to 0.9.5 or later from a previous version, you should first
uninstall the old version. To do that, run:

```
pip uninstall django-dbsettings
pip install dbsettings
```