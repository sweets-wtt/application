/** 实时客户端测试 */
import { describe, expect, it, vi } from "vitest";
import { RealtimeClient, type Ticket, type Transport } from "../src/index";

// 伪造传输：记录发送并暴露回调
class FakeTransport implements Transport {
  sent: string[] = [];
  closed = false;

  private onMessage: ((data: string) => void) | undefined;
  private onClose: ((error?: unknown) => void) | undefined;

  connect(onMessage: (data: string) => void, onClose: (error?: unknown) => void): void {
    this.onMessage = onMessage;
    this.onClose = onClose;
  }

  send(data: string): void {
    this.sent.push(data);
  }

  close(): void {
    this.closed = true;
  }

  emit(data: string): void {
    this.onMessage?.(data);
  }

  drop(): void {
    this.onClose?.();
  }
}

// 装配客户端与传输工厂
const harness = (queueLimit?: number) => {
  const transports: FakeTransport[] = [];
  const tickets: Ticket[] = [];
  const applyTicket = vi.fn();
  const onEvent = vi.fn();
  const client = new RealtimeClient({
    transport: () => {
      const transport = new FakeTransport();
      transports.push(transport);
      return transport;
    },
    acquireTicket: () => {
      const ticket: Ticket = {
        ticket: `t${tickets.length + 1}`,
        expiresAtMs: Date.now() + 30_000,
      };
      tickets.push(ticket);
      return Promise.resolve(ticket);
    },
    applyTicket,
    onEvent,
    queueLimit,
  });

  return { client, transports, tickets, applyTicket, onEvent };
};

// 连接就绪
const ready = async (client: RealtimeClient) => {
  vi.useFakeTimers();
  client.connect();
  await vi.advanceTimersByTimeAsync(0);
};

describe("连接", () => {
  it("票据获取后进入 connected 并应用票据", async () => {
    const { client, transports, tickets, applyTicket } = harness();

    await ready(client);

    expect(client.status).toBe("connected");
    expect(tickets).toEqual([{ ticket: "t1", expiresAtMs: tickets[0].expiresAtMs }]);
    expect(applyTicket).toHaveBeenCalledWith(transports[0], "t1");
  });
});

describe("发送", () => {
  it("已连接直发", async () => {
    const { client, transports } = harness();

    await ready(client);
    client.send("a");

    expect(transports[0].sent).toEqual(["a"]);
  });

  it("未连接入有界队列，连接后冲刷", async () => {
    const { client, transports } = harness(3);

    client.send("m1");
    client.send("m2");
    client.send("m3");
    client.send("m4");

    await ready(client);

    expect(transports[0].sent).toEqual(["m2", "m3", "m4"]);
  });
});

describe("心跳", () => {
  it("按间隔发送心跳", async () => {
    const { client, transports } = harness();

    await ready(client);
    await vi.advanceTimersByTimeAsync(15_000);
    expect(transports[0].sent).toEqual(["ping"]);

    await vi.advanceTimersByTimeAsync(15_000);
    expect(transports[0].sent).toEqual(["ping", "ping"]);
  });
});

describe("契约事件校验", () => {
  it("契约事件触发 onEvent", async () => {
    const { client, transports, onEvent } = harness();

    await ready(client);
    transports[0].emit('{"code":0,"message":"ok","data":{}}');

    expect(onEvent).toHaveBeenCalledWith({
      code: 0,
      message: "ok",
      data: {},
    });
  });

  it("非契约事件丢弃", async () => {
    const { client, transports, onEvent } = harness();

    await ready(client);
    transports[0].emit('{"oops":true}');

    expect(onEvent).not.toHaveBeenCalled();
  });
});

describe("票据续用", () => {
  it("到期前余量重新获取并应用", async () => {
    const { client, tickets, applyTicket, transports } = harness();

    await ready(client);
    await vi.advanceTimersByTimeAsync(25_000);

    expect(tickets).toHaveLength(2);
    expect(applyTicket).toHaveBeenLastCalledWith(transports[0], "t2");
  });
});

describe("断线重连", () => {
  it("断线后有界退避重连", async () => {
    const { client, transports, tickets } = harness();

    await ready(client);
    transports[0].drop();
    expect(client.status).toBe("disconnected");

    await vi.advanceTimersByTimeAsync(500);

    expect(transports).toHaveLength(2);
    expect(client.status).toBe("connected");
    expect(tickets).toHaveLength(2);
  });

  it("主动 close 不重连", async () => {
    const { client, transports } = harness();

    await ready(client);
    client.close();

    await vi.advanceTimersByTimeAsync(60_000);

    expect(transports).toHaveLength(1);
    expect(client.status).toBe("disconnected");
  });
});
