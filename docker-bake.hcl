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

// 目标组
group "apps" {
	// 目标列表
	targets = ["server"]
}

// 构建目标
target "server" {
	// 构建上下文
	context = "."
	// Dockerfile 路径
	dockerfile = "apps/server/Dockerfile"
	// 镜像标签
	tags = REGISTRY == "" ? ["server:latest"] : ["${REGISTRY}/server:${TAG}"]
	// 输出（官方：type=image 且 push=true 推送仓库）
	output = REGISTRY == "" ? ["type=docker"] : ["type=image,push=true"]
	// 证明（官方：SBOM 与来源证明随推送附带）
	attest = REGISTRY == "" ? [] : ["type=provenance,mode=max", "type=sbom"]
	// 构建期密钥（官方：BuildKit secret，Dockerfile 经 --mount=type=secret 消费）
	secret = REGISTRY == "" ? [] : ["id=github-token,env=GITHUB_TOKEN"]
}
