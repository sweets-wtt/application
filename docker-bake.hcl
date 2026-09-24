// Docker Bake - `https://docs.docker.com/build/bake/`

// 镜像仓库
variable "REGISTRY" {
	// 默认（本地 Docker）
	default = ""
}

// 镜像标签
variable "TAG" {
	// 默认（latest）
	default = "latest"
}
