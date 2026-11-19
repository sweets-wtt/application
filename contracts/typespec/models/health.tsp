namespace Application;

@doc("存活数据")
@example(#{ status: "ok" })
model HealthzData {
  @doc("存活状态取值")
  @example("ok")
  status: "ok";
}

@doc("存活响应")
@example(#{ code: 0, message: "ok", data: #{ status: "ok" } })
model HealthzResponse is Response<HealthzData>;
