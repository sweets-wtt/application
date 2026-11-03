"""契约生成物规范化 - 统一行尾为 LF"""

from pathlib import Path

# 生成物路径
TARGET = Path("packages/python/contracts/src/app/contracts/generated/http.py")


def main() -> None:
    """把 CRLF 统一为 LF"""
    data = TARGET.read_bytes().replace(b"\r\n", b"\n")
    TARGET.write_bytes(data)


if __name__ == "__main__":
    main()
