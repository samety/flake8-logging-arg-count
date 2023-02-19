import ast
import textwrap

from logging_arg_count import LoggingArgCountChecker


def test_log_statement_with_fewer_args_than_limit():
    code = """
        import logging
        logging.info("Hello, %s", "world")
    """
    tree = ast.parse(textwrap.dedent(code))
    checker = LoggingArgCountChecker(tree=tree, filename='fake_file.py')
    errors = list(checker.run())
    assert len(errors) == 0


def test_log_statement_with_more_args_than_limit():
    code = """
        import logging
        logging.info("Hello, %s %s %s", "world", "and")
    """
    tree = ast.parse(textwrap.dedent(code))
    checker = LoggingArgCountChecker(tree=tree, filename='fake_file.py')
    errors = list(checker.run())
    assert len(errors) == 1
    lineno, _, msg, _ = errors[0]
    assert lineno == 3
    assert msg == 'LAC001 info() call has 2 arguments but 3 "%s" placeholders in the log message'


def test_non_log_statement():
    code = """
        x = 1 + 2
    """
    tree = ast.parse(textwrap.dedent(code))
    checker = LoggingArgCountChecker(tree=tree, filename='fake_file.py')
    errors = list(checker.run())
    assert len(errors) == 0
