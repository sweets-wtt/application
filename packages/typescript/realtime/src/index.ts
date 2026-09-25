/** 传输无关实时客户端 */
import { Response } from "@app/contracts/src/schemas";

// 状态
export type Status = "disconnected" | "connecting" | "connected";

// 传输接口：由应用注入（web 注入 WebSocket，miniapp 注入 uni.connectSocket）
export interface Transport {
  // 建立连接并挂接回调
  connect(
    onMessage: (data: string) => void,
    onClose: (error?: unknown) => void,
    onError: (error: unknown) => void,
  ): void;
  // 发送文本
  send(data: string): void;
  // 关闭连接
  close(): void;
}

// 票据
export interface Ticket {
  // 票据
  ticket: string;
  // 过期时间（epoch 毫秒）
  expiresAtMs: number;
}

// 装配参数
export interface RealtimeOptions {
  // 传输工厂：每次连接调用
  transport: () => Transport;
  // 30 秒票据获取
  acquireTicket: () => Promise<Ticket>;
  // 票据应用：连接时与续用时调用
  applyTicket: (transport: Transport, ticket: string) => void;
  // 契约事件回调
  onEvent?: (event: unknown) => void;
  // 心跳间隔毫秒
  heartbeatIntervalMs?: number;
  // 重连退避基数毫秒
  backoffBaseMs?: number;
  // 重连退避上限毫秒
  backoffCapMs?: number;
  // 出站队列上限
  queueLimit?: number;
}

// 默认心跳间隔毫秒
const DEFAULT_HEARTBEAT_MS = 15_000;

// 默认退避基数毫秒
const DEFAULT_BACKOFF_BASE_MS = 500;

// 默认退避上限毫秒
const DEFAULT_BACKOFF_CAP_MS = 30_000;

// 默认出站队列上限
const DEFAULT_QUEUE_LIMIT = 100;

// 票据续用余量毫秒
const TICKET_RENEW_MARGIN_MS = 5_000;

// 定时器
type Timer = ReturnType<typeof setTimeout>;

export class RealtimeClient {
  // 状态
  status: Status = "disconnected";

  private readonly transportFactory: () => Transport;
  private readonly acquireTicket: () => Promise<Ticket>;
  private readonly applyTicket: (transport: Transport, ticket: string) => void;
  private readonly onEvent: ((event: unknown) => void) | undefined;
  private readonly heartbeatMs: number;
  private readonly backoffBase: number;
  private readonly backoffCap: number;
  private readonly queueLimit: number;

  // 当前传输
  private transport: Transport | undefined;
  // 出站队列
  private queue: string[] = [];
  // 重连次数
  private attempts = 0;
  // 主动关闭标记
  private closed = false;
  // 心跳定时器
  private heartbeatTimer: Timer | undefined;
  // 重连定时器
  private reconnectTimer: Timer | undefined;
  // 票据续用定时器
  private ticketTimer: Timer | undefined;

  constructor(options: RealtimeOptions) {
    this.transportFactory = options.transport;
    this.acquireTicket = options.acquireTicket;
    this.applyTicket = options.applyTicket;
    this.onEvent = options.onEvent;
    this.heartbeatMs = options.heartbeatIntervalMs ?? DEFAULT_HEARTBEAT_MS;
    this.backoffBase = options.backoffBaseMs ?? DEFAULT_BACKOFF_BASE_MS;
    this.backoffCap = options.backoffCapMs ?? DEFAULT_BACKOFF_CAP_MS;
    this.queueLimit = options.queueLimit ?? DEFAULT_QUEUE_LIMIT;
  }

  /** 建立连接：先获取票据，连接后冲刷队列并启用心跳 */
  connect(): void {
    if (this.closed || this.status !== "disconnected") {
      return;
    }
    this.status = "connecting";
    this.acquireTicket()
      .then(({ ticket, expiresAtMs }) => {
        if (this.closed || this.status !== "connecting") {
          return;
        }
        this.transport = this.transportFactory();
        this.transport.connect(
          (data) => this.receive(data),
          (error) => this.handleClose(error),
          () => undefined,
        );
        this.applyTicket(this.transport, ticket);
        this.status = "connected";
        this.attempts = 0;
        this.startHeartbeat();
        this.flushQueue();
        this.scheduleTicketRenewal(ticket, expiresAtMs);
      })
      .catch(() => this.scheduleReconnect());
  }

  /** 发送：已连接直发，否则入有界队列 */
  send(data: string): void {
    if (this.status === "connected" && this.transport !== undefined) {
      this.transport.send(data);
      return;
    }
    if (this.queue.length >= this.queueLimit) {
      this.queue.shift();
    }
    this.queue.push(data);
  }

  /** 关闭：主动关闭不重连 */
  close(): void {
    this.closed = true;
    this.clearTimers();
    this.transport?.close();
    this.transport = undefined;
    this.status = "disconnected";
  }

  /** 接收：契约事件校验，非契约事件丢弃 */
  private receive(data: string): void {
    try {
      this.onEvent?.(Response.parse(JSON.parse(data) as unknown));
    } catch {
      // 非契约事件丢弃
    }
  }

  /** 断线处理：停心跳并调度退避重连 */
  private handleClose(_error?: unknown): void {
    this.stopHeartbeat();
    this.transport = undefined;
    this.status = "disconnected";
    this.scheduleReconnect();
  }

  /** 有界退避重连 */
  private scheduleReconnect(): void {
    if (this.closed || this.reconnectTimer !== undefined) {
      return;
    }
    this.attempts += 1;
    const delay = Math.min(this.backoffCap, this.backoffBase * 2 ** (this.attempts - 1));
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = undefined;
      this.connect();
    }, delay);
  }

  /** 心跳 */
  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      this.transport?.send("ping");
    }, this.heartbeatMs);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer !== undefined) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = undefined;
    }
  }

  private clearTimers(): void {
    this.stopHeartbeat();
    if (this.reconnectTimer !== undefined) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = undefined;
    }
    if (this.ticketTimer !== undefined) {
      clearTimeout(this.ticketTimer);
      this.ticketTimer = undefined;
    }
  }

  /** 冲刷出站队列 */
  private flushQueue(): void {
    const queued = this.queue.splice(0, this.queue.length);
    for (const data of queued) {
      this.transport?.send(data);
    }
  }

  /** 票据续用：到期前余量重新获取并应用到当前传输 */
  private scheduleTicketRenewal(ticket: string, expiresAtMs: number): void {
    if (this.closed) {
      return;
    }
    const delay = Math.max(0, expiresAtMs - TICKET_RENEW_MARGIN_MS - Date.now());
    this.ticketTimer = setTimeout(() => {
      this.ticketTimer = undefined;
      if (this.closed || this.status !== "connected") {
        return;
      }
      this.acquireTicket()
        .then(({ ticket: next, expiresAtMs: nextExpiry }) => {
          if (this.closed || this.status !== "connected" || this.transport === undefined) {
            return;
          }
          this.applyTicket(this.transport, next);
          this.scheduleTicketRenewal(next, nextExpiry);
        })
        .catch(() => {
          // 静默：退避上限后重试，避免风暴
          this.scheduleTicketRenewal(ticket, Date.now() + this.backoffCap);
        });
    }, delay);
  }
}
