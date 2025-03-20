# -*- coding: utf-8 -*-
import os
from a3py.simplified.case import camel2snake


_MODEL_IMPORT = """
from ..models import {model_name}
"""

_CLASS_AND_META = """
class {model_name}Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = {model_name}
"""

_COMMON_FIELD = """
    {field_name} = {fake_expression}
"""

_FK_FIELD = """
    {field_name} = factory.SubFactory({related_factory_name})
"""

_M2M_FIELD = """
    @factory.post_generation
    def {field_name}(self, create, extracted, **_):
        if not create:
            return

        if extracted:
            for o in extracted:
                self.{field_name}.add(o)
"""


def build_triple_quote(
    s: str, format_dict: dict | None = None, clean_left: bool = True, clean_right: bool = False
) -> str:
    if clean_left:
        s = s[1:]
    if clean_right:
        s = s[:-1]
    if format_dict is not None:
        s = s.format(**format_dict)
    return s


class FactoryTemplate:
    def __init__(self):
        self._import_set = set()
        self._local_import_lines = list()
        self._abs_import_lines = list()
        self._content_lines = list()

    def import_custom_lib(self, lib: str):
        if lib in self._import_set:
            return

        self._import_set.add(lib)
        if lib.startswith("from ."):
            self._local_import_lines.append(lib)
        else:
            self._abs_import_lines.append(lib)

    def _import_model(self, model_name: str):
        self._local_import_lines.append(build_triple_quote(_MODEL_IMPORT, {"model_name": model_name}, clean_left=False))

    def import_related_factory(self, related_app_name: str, related_factory_name: str, current_app_name: str):
        if related_app_name == current_app_name:
            factory_filename = camel2snake(related_factory_name)
            s = f"from .{factory_filename} import {related_factory_name}"
        else:
            s = f"from {related_app_name}.factories import {related_factory_name}"

        self.import_custom_lib(s)

    def add_class_and_meta(self, model_name: str):
        self._content_lines.append(build_triple_quote(_CLASS_AND_META, {"model_name": model_name}, clean_left=False))

    def add_common_field(self, field_name: str, fake_expression: str):
        self._content_lines.append(
            build_triple_quote(
                _COMMON_FIELD,
                {
                    "field_name": field_name,
                    "fake_expression": fake_expression,
                },
                clean_right=True,
            )
        )

    def add_fk_field(self, field_name: str, related_factory_name: str):
        self._content_lines.append(
            build_triple_quote(
                _FK_FIELD,
                {
                    "field_name": field_name,
                    "related_factory_name": related_factory_name,
                },
                clean_right=True,
            )
        )

    def add_m2m_field(self, field_name: str):
        self._content_lines.append(build_triple_quote(_M2M_FIELD, {"field_name": field_name}, clean_left=False))

    def save(self, folder: str, model_name: str):
        self._import_model(model_name)
        self._abs_import_lines.insert(0, "import factory")

        filename = f"{camel2snake(model_name)}_factory.py"
        with open(os.path.join(folder, filename), "w", encoding="utf-8") as fd:
            lines = list()
            lines.extend(self._abs_import_lines)
            lines.extend(self._local_import_lines)
            lines.extend(self._content_lines)
            content = "\n".join(lines)
            if content[-1] != "\n":
                content += "\n"
            fd.write(content)
