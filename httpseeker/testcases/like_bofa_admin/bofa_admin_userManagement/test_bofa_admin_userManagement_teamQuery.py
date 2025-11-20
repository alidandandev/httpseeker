#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from httpseeker.common.send_request import send_request
from httpseeker.utils.request.case_data_parse import get_testcase_data

ddt_data, ids = get_testcase_data(filename='test_bofa_admin_userManagement_teamQuery.yaml')


class TestBofaAdminUsermanagementTeamquery:
    """BofaAdminUsermanagementTeamquery"""

    @pytest.mark.parametrize('case_data', ddt_data, ids=ids)
    def test_bofa_admin_userManagement_teamQuery(self, case_data):
        """test_bofa_admin_userManagement_teamQuery"""
        send_request.send_request(case_data)
