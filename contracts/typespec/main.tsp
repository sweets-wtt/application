import "@typespec/http";
import "@typespec/openapi";
import "./models/response.tsp";
import "./models/health.tsp";
import "./routes/health.tsp";

using TypeSpec.Http;
using TypeSpec.OpenAPI;

@service(#{ title: "API" })
@info(#{ version: "0.1.0" })
@server("/", "API server")
@doc("HTTP API 契约")
@tagMetadata("health", #{ description: "服务健康检查相关接口" })
namespace Application;
