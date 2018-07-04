from fused_home.interfaces.switch import OnOff


class AirCon(OnOff):
    def set_temperature(self, value, celsius=True):
        assert 15 < value < 30
        assert isinstance(celsius, bool)
        raise NotImplemented

    def set_intensity(self, value):
        assert 0 <= value <= 1
        raise NotImplemented
