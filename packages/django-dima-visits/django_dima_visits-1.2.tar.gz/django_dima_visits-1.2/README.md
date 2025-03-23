
# Django Dima Visits

## Installation

Installation is simple:  
1. `pip install django-dima-visits`  
2. Add `'visits'` or `'visits.apps.VisitsConfig'` to `INSTALLED_APPS` in `settings.py`  
3. Add `'visits.middleware.VisitMiddleware'` to `MIDDLEWARE` in `settings.py` like this:

```python
MIDDLEWARE = [
    ...
    'visits.middleware.VisitMiddleware',  # اضافه کردن میدل‌ور شما
]
```

After that, you can check visits in the Django admin panel.

## Change Log

**1.2**: Added Persian translation including PO and MO files in the app. Also added installation guide in the README.  
**1.0**: First release.
