import yeelight

from fused_home.interfaces.color_lamp import ColorLamp


class YeelightWhiteBulb(ColorLamp):
    def __init__(self, ip, model='mono1', port=55443, effect="smooth", duration=300):
        super(YeelightWhiteBulb, self).__init__(ip, port, model=model, effect=effect, duration=duration)
        self.bulb = yeelight.Bulb(ip, port=port, effect=effect, duration=duration, model=model)

    def on(self):
        self.bulb.turn_on()

    def off(self):
        self.bulb.turn_off()

    def set_percentage(self, value, force_on=False):
        assert 0 <= value <= 1
        int_value = int(100 * value)
        self.bulb.auto_on = force_on
        self.bulb.set_brightness(int_value)


class YeelightColorBulb(YeelightWhiteBulb):
    def __init__(self, ip, model='color1', port=55443, effect="smooth", duration=300):
        super(YeelightColorBulb, self).__init__(ip, model=model, port=port, effect=effect, duration=duration)

    def set_rgb(self, red, green, blue, force_on=False):
        self.bulb.auto_on = force_on
        self.bulb.set_rgb(red, green, blue)

    def set_color_temp(self, value, force_on=False):
        self.bulb.auto_on = force_on
        self.bulb.set_color_temp(value)

    def set_hsv(self, hue, saturation, value=None, force_on=False):
        self.bulb.auto_on = force_on
        self.bulb.set_hsv(hue, saturation, value)
