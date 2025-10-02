#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import unique

from httpseeker.enums import StrEnum


@unique
class SqlType(StrEnum):
    select = 'SELECT'
    insert = 'INSERT'
    update = 'UPDATE'
    delete = 'DELETE'
