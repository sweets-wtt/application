// 镜像仓库
variable "REGISTRY" {
  default = ""
}

// 镜像标签
variable "TAG" {
  default = "latest"
}

// 应用组
group "apps" {
  targets = []
}
