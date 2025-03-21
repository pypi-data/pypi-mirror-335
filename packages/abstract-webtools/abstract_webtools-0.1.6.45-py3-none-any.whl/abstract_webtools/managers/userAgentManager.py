from ..abstract_webtools import *
import random
operating_systems = ['Macintosh','Windows','Linux']
browsers = ['Firefox','Chrome','IceDragon','Waterfox','Gecko','Safari','MetaSr']
def get_browser(browser=None):
    if not browser:
        return browsers[0]
    if browser in browsers:
        return browser
    browser_lower = browser.lower()
    for string_browser in browsers:
        string_browser_lower = string_browser.lower()
        if string_browser in string_browser_lower:
            return string_browser
    return browsers[0]
def get_os(os=None):
    os_lower = os.lower()
    if not os:
        return operating_systems[0]
    for string_os in operating_systems:
        string_os_lower = string_os.lower()
        if string_os in string_os_lower:
            return string_os
    return operating_systems[0]
class UserAgentManager:
    def __init__(self, os=None, browser=None, version=None,user_agent=None):
        self.os = os or get_os(os=os)
        self.browser = browser or get_browser(browser=browser)
        self.version = version or '42.0'
        self.user_agent = user_agent or self.get_user_agent()
        self.header = self.user_agent_header()
    @staticmethod
    def user_agent_db():
        from ..big_user_agent_list import big_user_agent_dict
        return big_user_agent_dict

    def get_user_agent(self):
        ua_db = self.user_agent_db()

        if self.os and self.os in ua_db:
            os_db = ua_db[self.os]
        else:
            os_db = random.choice(list(ua_db.values()))

        if self.browser and self.browser in os_db:
            browser_db = os_db[self.browser]
        else:
            browser_db = random.choice(list(os_db.values()))

        if self.version and self.version in browser_db:
            return browser_db[self.version]
        else:
            return random.choice(list(browser_db.values()))

    def user_agent_header(self):
        return {"user-agent": self.user_agent}
class UserAgentManagerSingleton:
    _instance = None
    @staticmethod
    def get_instance(user_agent=UserAgentManager().get_user_agent()[0]):
        if UserAgentManagerSingleton._instance is None:
            UserAgentManagerSingleton._instance = UserAgentManager(user_agent=user_agent)
        elif UserAgentManagerSingleton._instance.user_agent != user_agent:
            UserAgentManagerSingleton._instance = UserAgentManager(user_agent=user_agent)
        return UserAgentManagerSingleton._instance
