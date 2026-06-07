from db.database import init_db
from services.log_parser import parse_log


def setup_module():
	init_db()


def test_parse_database_error():
	result = parse_log("2026-06-06 13:41:52 ERROR database connection failed")

	assert result["line_count"] == 1
	assert result["timestamp"] == "2026-06-06 13:41:52"
	assert result["severity"] == "ERROR"
	assert result["component"] == "database"


def test_parse_multiline_log():
	raw_log = "ERROR database connection failed\nWARN retrying connection\nINFO service started"

	result = parse_log(raw_log)

	assert result["line_count"] == 3
	assert result["severity"] == "ERROR"
	assert result["component"] == "database"


def test_parse_unknown_log():
	result = parse_log("hello world")

	assert result["severity"] == "UNKNOWN"
	assert result["component"] == "unknown"