// Docker Bake - https://docs.docker.com/build/bake/

// 镜像仓库（官方：设置后目标推送 registry，产出 repository@sha256）
variable "REGISTRY" {
	// 默认空：本地构建载入 Docker
	default = ""
}

// 镜像标签（官方：推送时的镜像版本标签）
variable "TAG" {
	// 默认 latest
	default = "latest"
}
