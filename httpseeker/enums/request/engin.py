#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpseeker.enums import StrEnum


class EnginType(StrEnum):
    requests = 'requests'
    httpx = 'httpx'
