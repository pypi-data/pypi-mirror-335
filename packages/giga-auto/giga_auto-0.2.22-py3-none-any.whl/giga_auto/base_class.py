from giga_auto.request import RequestBase


class ApiBase(RequestBase):
    def __init__(self, **env):
        self.host = env['host']
        super().__init__(self.host, env.get('expect_code', 200))
        self.headers = env['headers']
