import ast
import textwrap

from logging_arg_count import LoggingArgCountChecker


def test_log_statement_with_fewer_args_than_limit() -> None:
    code = """
        import logging
        logging.info("Hello, %s", "world")
    """
    tree = ast.parse(textwrap.dedent(code))
    checker = LoggingArgCountChecker(tree=tree, filename='fake_file.py')
    errors = list(checker.run())
    assert len(errors) == 0


def test_log_statement_with_more_args_than_limit() -> None:
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
    assert msg == 'LAC001 info() call has 2 arguments but 3 "%" placeholders in the log message'


def test_all_log_statement_with_more_args_than_limit() -> None:
    code = """
        import logging
        logging.critical("Hello, %s %s %s", "world", "and")
        logging.error("Hello, %s %s %s", "world", "and")
        logging.warning("Hello, %s %s %s", "world", "and")
        logging.info("Hello, %s %s %s", "world", "and")
        logging.debug("Hello, %s %s %s", "world", "and")
    """
    tree = ast.parse(textwrap.dedent(code))
    checker = LoggingArgCountChecker(tree=tree, filename='fake_file.py')
    errors = list(checker.run())
    assert len(errors) == 5


def test_non_log_statement() -> None:
    code = """
        x = 1 + 2
    """
    tree = ast.parse(textwrap.dedent(code))
    checker = LoggingArgCountChecker(tree=tree, filename='fake_file.py')
    errors = list(checker.run())
    assert len(errors) == 0


def test_not_logging_module_expect_no_error() -> None:
    code = """
        import abc
        abc.warning("Hello, %s", 1, 2)
    """
    tree = ast.parse(textwrap.dedent(code))
    checker = LoggingArgCountChecker(tree=tree, filename='fake_file.py')
    errors = list(checker.run())
    assert len(errors) == 0


def test_log_statement_with_standard_get_logger() -> None:
    code = """
        import logging
        abc = logging.getLogger()
        abc.info("Hello, %s", "world", "and")
    """
    tree = ast.parse(textwrap.dedent(code))
    checker = LoggingArgCountChecker(tree=tree, filename='fake_file.py')
    errors = list(checker.run())
    assert len(errors) == 1
    lineno, _, msg, _ = errors[0]
    assert lineno == 4
    assert msg == 'LAC001 info() call has 2 arguments but 1 "%" placeholders in the log message'


def test_log_statement_with_only_get_logger() -> None:
    code = """
        from logging import get_logger
        abc = get_logger()
        abc.info("Hello, %s", "world", "and")
    """
    tree = ast.parse(textwrap.dedent(code))
    checker = LoggingArgCountChecker(tree=tree, filename='fake_file.py')
    errors = list(checker.run())
    assert len(errors) == 1
    lineno, _, msg, _ = errors[0]
    assert lineno == 4
    assert msg == 'LAC001 info() call has 2 arguments but 1 "%" placeholders in the log message'
