namespace Application;

@doc("响应信封")
model Response<T> {
  @doc("业务状态码")
  code: int32;

  @doc("提示信息")
  message: string;

  @doc("业务数据")
  data: T;
}
