import ast
from typing import Iterator, Optional


LOG_METHODS = ['debug', 'info', 'warning', 'warn', 'error', 'critical']


def _optional_get_method_name(value: ast.Call) -> Optional[str]:
    if isinstance(value.func, ast.Attribute) and isinstance(value.func.attr, str):
        return value.func.attr.lower()
    if isinstance(value.func, ast.Name) and isinstance(value.func.id, str):
        return value.func.id.lower()
    return None


def _optional_get_logger_name(node: ast.Assign) -> Optional[str]:
    if not isinstance(node.value, ast.Call):
        return None

    if not (get_method_name := _optional_get_method_name(node.value)):
        return None

    if 'logger' not in get_method_name:
        return None

    if len(node.targets) != 1:
        return None

    return getattr(node.targets[0], 'id', None)


class LoggingArgCountChecker:
    name = 'flake8-logging-arg-count'
    version = '0.4.1'

    def __init__(self, tree: ast.Module, filename: str) -> None:
        self.tree = tree
        self.filename = filename
        self._loggers: list[str] = ['logging', 'logger']

    def _process_node(self, node: ast.AST) -> None:
        if not isinstance(node, ast.Assign):
            return

        if logger_name := _optional_get_logger_name(node):
            self._loggers.append(logger_name)

    def run(self) -> Iterator[tuple[int, int, str, type]]:
        for node in ast.walk(self.tree):
            self._process_node(node)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                func_id = getattr(node.func.value, 'id', None)
                if func_id not in self._loggers:
                    continue
                if node.func.attr not in LOG_METHODS:
                    continue
                log_msg_node = node.args[0]
                if isinstance(log_msg_node, ast.Constant) and isinstance(log_msg_node.value, str):
                    num_subs = log_msg_node.value.count('%')
                    num_args = len(node.args) - 1
                    if num_args == 0:
                        continue
                    if num_args != num_subs:
                        msg = f'LAC001 {node.func.attr}() call has {num_args} arguments but {num_subs} "%" placeholders in the log message'  # noqa: E501
                        yield node.lineno, node.col_offset, msg, type(self)
