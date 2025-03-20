# dj3fb

English | [简体中文](README_ZH.md)

`dj3fb` can generate `DjangoModelFactory` for your django models by using `factory_boy`.

## 1. Introduction

* `dj3fd` is a Django app that has a command `generate_factories`, which can generate `DjangoModelFactory` classes based on Django models.
* There is a variable `f` in `faker_utils`, which is an instance of `Faker` and can be used to generate random data.

## 2. Usage

### Install

```shell
pip install dj3fb

```
### Examples

* Configure `settings.py`

```python
INSTALLED_APPS = [
    '...',
    'dj3fb',
    '...'
]

# Optional.
DJ3FB = {
    # Optional.Generate factory classes for django built-in apps or third-party apps.
    "include_third_party_apps": [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ],
    # Optional.Manually specify a factory class for a model instead of generating it automatically.
    "existed_factories": {
        "django.contrib.auth.User": "test_app.UserFactory"
    },
}


```

* Execute the command: `generate_factories`

```shell
python manage.py generate_factories
# In the app directory, a factories directory will be generated, which contains factory classes generated based on the models.

```
