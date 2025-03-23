class KeepAlivedConfigConstants:
    DEFAULT_PATH = "/etc/keepalived/keepalived.conf"
    INDENT_WIDTH = 4

    @staticmethod
    def get_indent(level: int = 0) -> str:
        return " " * (KeepAlivedConfigConstants.INDENT_WIDTH * level)
