#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from httpseeker.common.send_request import send_request
from httpseeker.utils.request.case_data_parse import get_testcase_data

ddt_data, ids = get_testcase_data(filename='test_volt_h5_register.yaml')


class TestVoltH5Register:
    """VoltH5Register"""

    @pytest.mark.parametrize('case_data', ddt_data, ids=ids)
    def test_volt_h5_register(self, case_data):
        """test_volt_h5_register"""
        send_request.send_request(case_data)
