class OnOff(object):
    def on(self):
        raise NotImplemented

    def off(self):
        raise NotImplemented


class OnOffPercentage(OnOff):
    def set_percentage(self, value, force_on=False):
        raise NotImplemented
