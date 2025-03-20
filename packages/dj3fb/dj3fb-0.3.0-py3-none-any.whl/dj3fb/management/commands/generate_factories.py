# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from dj3fb.services.generate_factories_service import GenerateFactoriesService


class Command(BaseCommand):
    def handle(self, *args, **options):
        GenerateFactoriesService().start()
