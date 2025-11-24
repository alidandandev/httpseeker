#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from httpseeker.common.send_request import send_request
from httpseeker.utils.request.case_data_parse import get_testcase_data

ddt_data, ids = get_testcase_data(filename='test_bofa_admin_systemManagement_deptManagement.yaml')


class TestBofaAdminSystemmanagementDeptmanagement:
    """BofaAdminSystemmanagementDeptmanagement"""

    @pytest.mark.parametrize('case_data', ddt_data, ids=ids)
    def test_bofa_admin_systemManagement_deptManagement(self, case_data):
        """test_bofa_admin_systemManagement_deptManagement"""
        send_request.send_request(case_data)
