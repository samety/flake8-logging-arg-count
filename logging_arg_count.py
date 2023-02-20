import ast
from typing import Iterator


LOG_METHODS = ['debug', 'info', 'warning', 'warn', 'error', 'critical']


class LoggingArgCountChecker:
    name = 'flake8-logging-arg-count'
    version = '0.2.0'

    def __init__(self, tree: ast.Module, filename: str) -> None:
        self.tree = tree
        self.filename = filename
        self._loggers: list[str] = ['logging']

    def _process_node(self, node: ast.AST) -> None:
        if not isinstance(node, ast.Assign):
            return

        if not isinstance(node.value, ast.Call):
            return

        if not isinstance(node.value.func, ast.Attribute):
            return

        module_name = getattr(node.value.func.value, 'id', None)
        if not module_name == 'logger':
            pass

        if not node.value.func.attr == 'getLogger':
            pass

        if len(node.targets) != 1:
            return

        logger_name = getattr(node.targets[0], 'id', None)
        if logger_name is not None:
            self._loggers.append(logger_name)

    def run(self) -> Iterator[tuple[int, int, str, type]]:
        for node in ast.walk(self.tree):
            self._process_node(node)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                func_id = getattr(node.func.value, 'id', None)
                if func_id not in self._loggers:
                    continue
                if node.func.attr in LOG_METHODS:
                    log_msg_node = node.args[0]
                    if isinstance(log_msg_node, ast.Str):
                        num_args = len(node.args) - 1
                        num_subs = log_msg_node.s.count('%s')
                        if num_args != num_subs:
                            msg = f'LAC001 {node.func.attr}() call has {num_args} arguments but {num_subs} "%s" placeholders in the log message'  # noqa: E501
                            yield node.lineno, node.col_offset, msg, type(self)
