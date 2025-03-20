"""
.. include:: ../README.md
   :start-line: 2
   :end-before: Contribution
"""

import logging
from pydantic_settings import BaseSettings


class Configs(BaseSettings):
    cors_methods: set[str] = ["*"]
    cors_headers: set[str] = ["*"]
    cors_origins: set[str] = ["*"]
    cors_allow_credentials: bool = True
    log_level: str = "DEBUG"
    oauth_issuer: str = ""
    oauth_domain: str = ""
    oauth_algorithms: str = ""
    oauth_audience: str = ""
    secret_key: str = "SUPER FUCKIN SECRET DONT WORRY ABOUT IT BUDDY"


configs = Configs()


logging.basicConfig(level=configs.log_level)
