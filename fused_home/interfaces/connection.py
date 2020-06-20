from dataclasses import dataclass
from typing import Optional


@dataclass
class HostPort:
    remote_host: Optional[str]
    remote_port: Optional[int]
    local_host: Optional[str]
    local_port: Optional[int]

    def get_pair_for_home(self, target_home, origin_home):
        if target_home == origin_home:
            return self.local_host, self.local_port
        else:
            return self.remote_host, self.remote_port
