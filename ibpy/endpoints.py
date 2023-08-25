from enum import StrEnum


class IBRestEndpoints(StrEnum):
    TICKLE = "/tickle"
    PORTFOLIO_ACCOUNTS = "/portfolio/accounts"
