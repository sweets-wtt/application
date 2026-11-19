import "@typespec/http";
import "@typespec/openapi";

using TypeSpec.Http;
using TypeSpec.OpenAPI;

namespace Application;

@tag("health")
@route("/healthz")
@get
@operationId("getHealthz")
@summary("存活探针")
@doc("返回服务存活状态")
@opExample(
  #{ returnType: #{ code: 0, message: "ok", data: #{ status: "ok" } } },
  #{ title: "存活响应", description: "服务正常时的响应示例" }
)
op getHealthz(): HealthzResponse;
