class OnOff(object):
    def __init__(self, ip, port=None, **kwargs):
        self.ip = ip
        self.port = port
        self.init(ip=ip, port=port, **kwargs)

    def on(self):
        raise NotImplemented

    def off(self):
        raise NotImplemented

    def init(self, **kwargs):
        pass


class OnOffPercentage(OnOff):
    def set_percentage(self, value, force_on=False):
        raise NotImplemented
