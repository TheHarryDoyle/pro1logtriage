from db.database import init_db
from services.triage_engine import triage_log


def setup_module():
	init_db()


def test_database_connection_issue():
	result = triage_log("ERROR database connection failed")

	assert result["category"] == "database_connection_issue"
	assert result["confidence"] == 0.85
	assert len(result["commands_to_check"]) > 0


def test_nginx_upstream_timeout():
	result = triage_log("ERROR nginx upstream timed out while connecting to backend")

	assert result["category"] == "nginx_upstream_timeout"


def test_disk_usage_full():
	result = triage_log("ERROR no space left on device")

	assert result["category"] == "disk_usage_full"


def test_unknown_log():
	result = triage_log("some random log line with nothing useful")

	assert result["category"] == "unknown"