# -*- coding: utf-8 -*-
# @Project: 芒果测试平台# @Description:
# @Time   : 2023/4/6 13:36
# @Author : 毛鹏
import json

from mangokit.tools.assertion.public_assertion import WhatIsItAssertion, ContainAssertion, MatchingAssertion, \
    WhatIsEqualToAssertion
from mangokit.uidrive.android import UiautomatorAssertion
from mangokit.uidrive.web.assertion import PlaywrightAssertion


class Assertion(WhatIsItAssertion, ContainAssertion, MatchingAssertion, WhatIsEqualToAssertion, PlaywrightAssertion,
                UiautomatorAssertion):
    pass


if __name__ == '__main__':
    print(json.dumps(Assertion.get_methods(), ensure_ascii=False))
