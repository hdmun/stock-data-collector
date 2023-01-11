from dataclasses import dataclass


@dataclass(frozen=True)
class WorkerConfig(object):
    kiwoom_addr: tuple[str, str]  # host, port
