# -*- coding: utf-8 -*-
import importlib.util
from typing import Dict, Type
from django.db import models

from dj3fb.services.generate_factories_service import field_templates as ft

_mappings: Dict[Type[models.Field], Type[ft.BaseFieldTemplate]] = {
    models.BigIntegerField: ft.BigIntegerFieldTemplate,
    models.BinaryField: ft.BinaryFieldTemplate,
    models.BooleanField: ft.BooleanFieldTemplate,
    models.CharField: ft.CharFieldTemplate,
    models.DateField: ft.DateFieldTemplate,
    models.DateTimeField: ft.DateTimeFieldTemplate,
    models.DecimalField: ft.DecimalFieldTemplate,
    models.DurationField: ft.DurationFieldTemplate,
    models.EmailField: ft.EmailFieldTemplate,
    models.FileField: ft.FileFieldTemplate,
    models.FilePathField: ft.FilePathFieldTemplate,
    models.FloatField: ft.FloatFieldTemplate,
    models.GenericIPAddressField: ft.GenericIPAddressFieldTemplate,
    models.ImageField: ft.ImageFieldTemplate,
    models.IntegerField: ft.IntegerFieldTemplate,
    models.JSONField: ft.JSONFieldTemplate,
    models.PositiveIntegerField: ft.IntegerFieldTemplate,
    models.PositiveBigIntegerField: ft.BigIntegerFieldTemplate,
    models.PositiveSmallIntegerField: ft.SmallIntegerFieldTemplate,
    models.SlugField: ft.CharFieldTemplate,
    models.SmallIntegerField: ft.IntegerFieldTemplate,
    models.TextField: ft.TextFieldTemplate,
    models.TimeField: ft.TimeFieldTemplate,
    models.URLField: ft.URLFieldTemplate,
    models.UUIDField: ft.UUIDFieldTemplate,
}

if importlib.util.find_spec("psycopg2") is not None:
    from django.contrib.postgres import fields as pg_fields

    _mappings.update(
        {
            # pg_fields
            pg_fields.ArrayField: ft.ArrayFieldTemplate,
        }
    )
    POSTGRES_SUPPORTED = True
else:
    POSTGRES_SUPPORTED = False


class FieldTemplateManager:
    cached_mappings: Dict[str, Type[ft.BaseFieldTemplate | ft.ArrayFieldTemplate]] = dict()
    mappings = _mappings

    @classmethod
    def get_field_template_instance(cls, field_instance: models.Field) -> ft.BaseFieldTemplate | ft.ArrayFieldTemplate:
        field_template_cls = cls._get_field_template_cls(type(field_instance))
        if POSTGRES_SUPPORTED:
            if isinstance(field_instance, pg_fields.ArrayField):
                base_field_template = cls.get_field_template_instance(field_instance.base_field)
                assert issubclass(field_template_cls, ft.ArrayFieldTemplate)
                return field_template_cls(field_instance, base_field_template)

        return field_template_cls(field_instance)

    @classmethod
    def _get_field_template_cls(cls, field_cls) -> Type[ft.BaseFieldTemplate | ft.ArrayFieldTemplate]:
        cls_name = field_cls.__name__

        cache_result = cls.cached_mappings.get(cls_name, None)
        if cache_result is not None:
            return cache_result

        for f_cls in field_cls.__mro__:
            json_field_cls = cls.mappings.get(f_cls, None)
            if json_field_cls is not None:
                cls.cached_mappings[cls_name] = json_field_cls
                return json_field_cls

        raise TypeError(f"{cls_name} can not find corresponding field class.")
