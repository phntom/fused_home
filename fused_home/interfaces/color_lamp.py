from fused_home.interfaces.switch import OnOffPercentage


class ColorLamp(OnOffPercentage):
    def set_rgb(self, red, green, blue, force_on=False):
        raise NotImplemented

    def set_color_temp(self, value, force_on=False):
        raise NotImplemented
