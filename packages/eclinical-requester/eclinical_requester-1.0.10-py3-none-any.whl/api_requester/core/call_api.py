# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 12/27/2024 2:59 PM
@Description: Description
@File: call_api.py
"""
from requests import request

from api_requester.dto.admin.user_on_board_dto import UserOnBoardDto
from api_requester.dto.biz_base import BizBase
from api_requester.dto.user import EClinicalUser
from api_requester.http.app_url import AppUrl
from api_requester.http.authorize import Authorize
from api_requester.utils.placeholder_replacer import PlaceholderReplacer


class ApiRequester(BizBase):

    def __init__(self, username=None, password=None, sponsor=None, study=None, test_env=None, app_env=None, app=None,
                 company=None, role=None, external=False):
        u = EClinicalUser(
            username=username,
            password=password,
            sponsor=sponsor,
            study=study,
            test_env=test_env,
            app_env=app_env,
            app=app,
            company=company,
            role=role,
            external=external
        )
        super().__init__(u)
        self.headers = dict()
        self.user_onboard_dto: UserOnBoardDto = UserOnBoardDto(-1)

    def login(self):
        auth = Authorize(self.user)
        auth.login()
        self.headers = auth.headers
        self.time_mills = auth.time_mills
        self.user_onboard_dto = auth.user_onboard_dto
        return self

    def request(self, method, api, **kwargs):
        if self.user.external is False:
            url = AppUrl(self.user.app, self.user.test_env).which_url(self.user.app)(api)
        else:
            url = AppUrl(self.user.app, self.user.test_env).external_url(api)
        request(method, url, headers=self.headers, **kwargs)

    def user_replacer(self):
        return PlaceholderReplacer({
            "Sponsor ID": self.user_onboard_dto.sponsorId,
            "Study ID": self.user_onboard_dto.studyId,
            "Env ID": self.user_onboard_dto.envId,
            "Sponsor Name": self.user.sponsor,
            "Study Name": self.user.study,
            "Lifecycle": self.user.app_env,
        })
