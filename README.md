# flake8-logging-arg-count

flake8 plugin that checks if the number of arguments is inline with the number of `%s` placeholders.

- For example:
	- This is OK\
	`logging.warning('My message %s', x)`

	- These will trigger `LAC101`\
	`logging.warning('My message %s', x, y)`\
	`logging.warning('My message %s %s', x)`
