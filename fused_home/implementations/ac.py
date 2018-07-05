from fused_home.interfaces.switch import OnOffPercentage


class AC(OnOffPercentage):
    def on(self):
        pass

    def off(self):
        pass

    def set_percentage(self, value, force_on=True):
        assert force_on
        pass
