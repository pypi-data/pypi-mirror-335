# -*- coding: utf-8 -*-
import os
from typing import List, Type, Optional
from collections import defaultdict
from django.conf import settings
from django.db import models
from django.apps import apps, AppConfig
from django.db.models.fields import AutoFieldMixin  # noqa
from django.db.models.fields.related import RelatedField
from django.db.models.options import Options
from a3py.simplified.case import camel2snake

from .factory_template import FactoryTemplate
from .field_template_manager import FieldTemplateManager

"""

DJ3FB = {
    "existed_factories": {
        'django.contrib.auth.User': 'local_app.UserFactory'
    },
    "include_third_party_apps": [
        'third_party_app'
    ]
}

"""


class GenerateFactoriesService:
    def __init__(self):
        conf = getattr(settings, "DJ3FB", dict())
        self.include_third_party_apps = conf.get("include_third_party_apps", list())
        self.existed_factories = conf.get("existed_factories", dict())

        self._app_label2factories = defaultdict(list)
        self._app_label2app_name = dict()

    def start(self):
        target_apps = self._get_target_apps()
        for app in target_apps:
            model_list = list(app.get_models())
            if len(model_list) == 0:
                continue

            factories_folder = self._ensure_factories_folder(app)
            for model in model_list:
                if self._check_existed_factory(model) is None:
                    self._build_model_factory(factories_folder, app, model)
            self._ensure_factories_package(factories_folder, app)

    def _check_existed_factory(self, model: Type[models.Model]) -> Optional[str]:
        app_label__model = f"{getattr(model, '_meta').app_config.name}.{model.__name__}"
        return self.existed_factories.get(app_label__model, None)

    def _build_model_factory(self, factories_folder: str, app: AppConfig, model: Type[models.Model]):
        def _get_related_factory_app(m: Type[models.Model]) -> AppConfig:
            meta: Options = getattr(m, "_meta")
            return meta.app_config

        template = FactoryTemplate()

        # fields
        common_fields = dict()
        fk_fields = dict()
        m2m_fields = dict()
        opts: Options = getattr(model, "_meta")

        for f in opts.get_fields():
            if isinstance(f, RelatedField):
                if isinstance(f, models.ManyToManyField):
                    m2m_fields[f.name] = f
                else:
                    fk_fields[f.name] = f

                    related_model = f.related_model

                    related_app__factory = self._check_existed_factory(related_model)
                    if related_app__factory is not None:
                        app_name, factory_name = related_app__factory.rsplit(".", 1)
                        template.import_related_factory(
                            related_app_name=app_name,
                            related_factory_name=factory_name,
                            current_app_name=self._app_label2app_name[app.label],
                        )
                    else:
                        related_app = _get_related_factory_app(related_model)
                        template.import_related_factory(
                            related_app_name=self._app_label2app_name[related_app.label],
                            related_factory_name=f"{related_model.__name__}Factory",
                            current_app_name=self._app_label2app_name[app.label],
                        )
            elif isinstance(f, models.Field):
                # remove auto_field, auto_now fields
                if isinstance(f, AutoFieldMixin) or not f.editable:
                    continue

                common_fields[f.name] = f

        # class
        template.add_class_and_meta(model.__name__)

        for field_name, field_instance in common_fields.items():
            field_template = FieldTemplateManager.get_field_template_instance(field_instance)
            custom_lib, fake_expression = field_template.get_fake_expression()
            template.add_common_field(field_name=field_name, fake_expression=fake_expression)
            if custom_lib is not None:
                template.import_custom_lib(custom_lib)

        for field_name, field_instance in fk_fields.items():
            template.add_fk_field(
                field_name=field_name, related_factory_name=f"{field_instance.related_model.__name__}Factory"
            )

        for field_name, field_instance in m2m_fields.items():
            template.add_m2m_field(field_name)

        template.save(folder=factories_folder, model_name=model.__name__)
        self._app_label2factories[app.label].append(f"{model.__name__}Factory")

    def _ensure_factories_package(self, factories_folder: str, app: AppConfig):
        lines = list()

        factories = self._app_label2factories[app.label]
        for factory_name in factories:
            line = f"from .{camel2snake(factory_name)} import {factory_name}"
            lines.append(line)

        for app__factory in self.existed_factories.values():
            app_name, factory_name = app__factory.rsplit(".", 1)
            if app_name == app.name:
                line = f"from .{camel2snake(factory_name)} import {factory_name}"
                lines.append(line)

        with open(os.path.join(factories_folder, "__init__.py"), "w", encoding="utf-8") as fd:
            content = "\n".join(lines) + "\n"
            fd.write(content)

    @classmethod
    def _ensure_factories_folder(cls, app: AppConfig) -> str:
        factories_dir = os.path.join(app.path, "factories")
        if not os.path.isdir(factories_dir):
            os.makedirs(factories_dir)
        return factories_dir

    def _get_target_apps(self) -> List[AppConfig]:
        target_apps = list()

        base_dir = str(settings.BASE_DIR)
        for app_name in settings.INSTALLED_APPS:
            app_label = str(app_name).split(".")[-1]
            self._app_label2app_name[app_label] = app_name
            app: AppConfig = apps.get_app_config(app_label)

            if str(app.path).startswith(base_dir):
                target_apps.append(app)
            else:
                # third-party
                if app_name in self.include_third_party_apps:
                    target_apps.append(app)

        return target_apps
