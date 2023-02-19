import ast


class LoggingArgCountChecker:
    name = 'flake8-logging-arg-count'
    version = '0.1.0'

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename

    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['debug', 'info', 'warning', 'error', 'critical']:
                        log_msg_node = node.args[0]
                        if isinstance(log_msg_node, ast.Str):
                            num_args = len(node.args) - 1
                            num_subs = log_msg_node.s.count('%s')
                            if num_args != num_subs:
                                yield node.lineno, node.col_offset, f'LAC001 {node.func.attr}() call has {num_args} arguments but {num_subs} "%s" substitutions in the log message', type(self)
                        else:
                            yield node.lineno, node.col_offset, f'LAC002 {node.func.attr}() call does not have a string log message', type(self)
