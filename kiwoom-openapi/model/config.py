from dataclasses import dataclass


@dataclass(frozen=True)
class Config(object):
    host: str
    echo_port: int
    push_port: int
