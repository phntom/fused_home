from fused_home.interfaces.switch import OnOffPercentage


class TV(OnOffPercentage):
    def on(self):
        pass

    def off(self):
        pass

    def set_percentage(self, value, force_on=False):
        pass

    def chromecast(self, url):
        pass
