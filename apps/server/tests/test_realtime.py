"""实时适配器与路由测试"""

from typing import TYPE_CHECKING, Any, cast

import pytest
from app.cache import CacheClient
from fastapi import FastAPI, HTTPException
from server.adapters import realtime
from server.routes.realtime import create_ticket

if TYPE_CHECKING:
    # 异步客户端 仅注解使用
    import valkey.asyncio as valkey


class StubValkey:
    """异步客户端桩 记录调用 返回固定值"""

    def __init__(self, *, exists: bool = True, conflict: bool = False) -> None:
        # GETDEL 时键是否存在
        self.exists = exists
        # SET NX 是否冲突
        self.conflict = conflict
        # 调用记录 (方法 位置参数 关键字参数)
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    async def set(
        self,
        key: str,
        value: str,
        *,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool:
        """记录写入结果 nx 冲突时返回 False"""
        self.calls.append(("set", (key, value), {"ex": ex, "nx": nx}))
        return not (nx and self.conflict)

    async def getdel(self, key: str) -> str | None:
        """记录并按存在性返回"""
        self.calls.append(("getdel", (key,), {}))
        return "1" if self.exists else None


def make_client(
    *,
    exists: bool = True,
    conflict: bool = False,
) -> tuple[CacheClient, StubValkey]:
    """桩客户端与桩实例 类型对齐适配器入参"""
    stub = StubValkey(exists=exists, conflict=conflict)
    return CacheClient(cast("valkey.Valkey", stub), "app"), stub
    return CacheClient(cast("valkey.Valkey", stub), "app"), stub


def test_new_ticket_is_256bit() -> None:
    """票据为 256 bit urlsafe 编码"""
    ticket = realtime.new_ticket()

    assert len(ticket) == 43
    assert all(c.isalnum() or c in "-_" for c in ticket)


async def test_issue_ticket() -> None:
    """签发以 SET NX EX 30 写入前缀键"""
    client, stub = make_client()
    ok = await realtime.issue_ticket(client, "t")

    assert ok is True
    assert stub.calls == [
        ("set", ("app:realtime:ticket:t", "1"), {"ex": 30, "nx": True})
    ]


async def test_issue_ticket_conflict() -> None:
    """票据已存在时签发返回 False"""
    client, stub = make_client(conflict=True)
    ok = await realtime.issue_ticket(client, "t")

    assert ok is False
    assert stub.calls == [
        ("set", ("app:realtime:ticket:t", "1"), {"ex": 30, "nx": True})
    ]


async def test_redeem_ticket() -> None:
    """核销以 GETDEL 一次性读取"""
    client, stub = make_client()
    ok = await realtime.redeem_ticket(client, "t")

    assert ok is True
    assert stub.calls == [("getdel", ("app:realtime:ticket:t",), {})]


async def test_redeem_ticket_missing() -> None:
    """票据不存在时核销返回 False"""
    client, _ = make_client(exists=False)

    assert await realtime.redeem_ticket(client, "t") is False


async def test_redeem_ticket_rejects_overlong() -> None:
    """超长票据直接拒绝 不触达客户端"""
    client, stub = make_client()
    ticket = "x" * (realtime.TICKET_MAX_LEN + 1)

    assert await realtime.redeem_ticket(client, ticket) is False
    assert stub.calls == []


async def test_create_ticket_allowed_origin() -> None:
    """允许列表内 Origin 签发成功"""
    client, _ = make_client()
    response = await create_ticket(cache=client, origin="https://app.example.com")

    assert response["code"] == 0
    assert len(response["data"]["ticket"]) == 43


async def test_create_ticket_rejects_origin() -> None:
    """列表外或缺省 Origin 返回 403"""
    client, stub = make_client()

    with pytest.raises(HTTPException) as exc:
        await create_ticket(cache=client, origin="https://evil.example.com")
    assert exc.value.status_code == 403

    with pytest.raises(HTTPException) as exc:
        await create_ticket(cache=client)
    assert exc.value.status_code == 403
    assert stub.calls == []


async def test_realtime_route_registered(app: FastAPI) -> None:
    """路由已注册于应用"""
    assert app.url_path_for("create_ticket") == "/realtime/tickets"
