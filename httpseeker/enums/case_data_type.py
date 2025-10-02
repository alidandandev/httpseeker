#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpseeker.enums import StrEnum


class CaseDataType(StrEnum):
    JSON = 'json'
    YAML = 'yaml'
    YML = 'yml'
