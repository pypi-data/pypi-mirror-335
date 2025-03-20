# -*- coding: utf-8 -*-
from faker import Faker
from lazy_object_proxy import Proxy
from a3py.simplified.env import get_str


def _faker() -> Faker:
    locale = get_str("FAKER_LOCALE", None)
    return Faker(locale=locale)


f: Faker = Proxy(_faker)
