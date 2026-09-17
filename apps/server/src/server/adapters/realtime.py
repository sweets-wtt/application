"""实时适配器"""

import secrets
from typing import Final

from app.cache import CacheClient

# 票据有效期秒数
TICKET_TTL: Final[int] = 30

# 票据键前缀
TICKET_PREFIX: Final[str] = "realtime:ticket"

# 票据最大长度
TICKET_MAX_LEN: Final[int] = 128


def _ticket_key(ticket: str) -> str:
    """票据键"""
    return f"{TICKET_PREFIX}:{ticket}"


def new_ticket() -> str:
    """生成 256 bit 一次性票据"""
    return secrets.token_urlsafe(32)


async def issue_ticket(cache: CacheClient, ticket: str) -> bool:
    """SET NX EX 30 写入票据 已存在时返回 False"""
    return await cache.set(_ticket_key(ticket), "1", ex=TICKET_TTL, nx=True)


async def redeem_ticket(cache: CacheClient, ticket: str) -> bool:
    """GETDEL 一次性核销 不存在或非法返回 False"""
    if not ticket or len(ticket) > TICKET_MAX_LEN:
        return False
    return await cache.getdel(_ticket_key(ticket)) is not None
