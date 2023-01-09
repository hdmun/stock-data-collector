#!/usr/bin/python3
# -*-coding: utf-8 -*-

from dataclasses import dataclass


@dataclass(frozen=True)
class JobConfig(object):
    kiwoom_addr: tuple[str, str]  # host, port
