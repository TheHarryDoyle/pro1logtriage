import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'app.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(	"""
		CREATE TABLE IF NOT EXISTS log_analyses (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			raw_log TEXT NOT NULL,
			line_count INTEGER NOT NULL,
			timestamp TEXT,
			severity TEXT NOT NULL,
			component TEXT NOT NULL,
			category TEXT NOT NULL,
			confidence REAL NOT NULL,
			suggested_actions TEXT NOT NULL,
			commands_to_check TEXT NOT NULL,
			analyzed_lines TEXT NOT NULL,
			created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
		)
		""")
    conn.commit()
	
    create_rule_tables(conn)
    seed_default_rules(conn)

    conn.close()

def create_rule_tables(connection):
	cursor = connection.cursor()

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS severity_levels (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL UNIQUE,
			priority INTEGER NOT NULL,
			enabled INTEGER NOT NULL DEFAULT 1
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS severity_keywords (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			severity_id INTEGER NOT NULL,
			keyword TEXT NOT NULL,
			FOREIGN KEY (severity_id) REFERENCES severity_levels(id) ON DELETE CASCADE,
			UNIQUE(severity_id, keyword)
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS component_rules (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			component TEXT NOT NULL UNIQUE,
			priority INTEGER NOT NULL,
			enabled INTEGER NOT NULL DEFAULT 1
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS component_keywords (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			component_rule_id INTEGER NOT NULL,
			keyword TEXT NOT NULL,
			FOREIGN KEY (component_rule_id) REFERENCES component_rules(id) ON DELETE CASCADE,
			UNIQUE(component_rule_id, keyword)
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS triage_rules (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			category TEXT NOT NULL UNIQUE,
			confidence REAL NOT NULL,
			suggested_actions TEXT NOT NULL,
			priority INTEGER NOT NULL,
			enabled INTEGER NOT NULL DEFAULT 1
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS triage_keywords (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			triage_rule_id INTEGER NOT NULL,
			keyword TEXT NOT NULL,
			FOREIGN KEY (triage_rule_id) REFERENCES triage_rules(id) ON DELETE CASCADE,
			UNIQUE(triage_rule_id, keyword)
		)
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS triage_commands (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			triage_rule_id INTEGER NOT NULL,
			command TEXT NOT NULL,
			command_order INTEGER NOT NULL,
			FOREIGN KEY (triage_rule_id) REFERENCES triage_rules(id) ON DELETE CASCADE
		)
		"""
	)

	connection.commit()


DEFAULT_SEVERITY_RULES = [
	("EMERGENCY", 0, ["EMERGENCY", "EMERG", "PANIC", "<0>"]),
	("ALERT", 1, ["ALERT", "<1>"]),
	("CRITICAL", 2, ["CRITICAL", "CRIT", "<2>"]),
	("ERROR", 3, ["ERROR", "ERR", "FAILED", "FAILURE", "<3>"]),
	("WARNING", 4, ["WARNING", "WARN", "<4>"]),
	("NOTICE", 5, ["NOTICE", "<5>"]),
	("INFO", 6, ["INFO", "INFORMATIONAL", "<6>"]),
	("DEBUG", 7, ["DEBUG", "DBG", "<7>"]),
]


DEFAULT_COMPONENT_RULES = [
	("nginx", 10, ["nginx", "upstream", "502", "504"]),
	("systemd", 20, ["systemd", ".service", "failed to start"]),
	("database", 30, ["database", "postgres", "postgresql", "mysql", "connection failed"]),
	("tls", 40, ["certificate", "tls", "ssl", "x509"]),
	("dns", 50, ["dns", "lookup", "resolve", "could not resolve", "name resolution"]),
	("disk", 60, ["disk", "no space left", "filesystem", "volume full"]),
	("permissions", 70, ["permission denied", "access denied"]),
	("network", 80, ["port", "address already in use", "connection refused", "timeout"]),
]


DEFAULT_TRIAGE_RULES = [
	{
		"category": "nginx_upstream_timeout",
		"priority": 10,
		"keywords": ["upstream timed out", "502", "504", "bad gateway"],
		"confidence": 0.90,
		"suggested_actions": "Check whether the backend service is healthy and reachable from nginx.",
		"commands_to_check": [
			"systemctl status nginx",
			"journalctl -u nginx -xe",
			"ss -tulpn",
		],
	},
	{
		"category": "database_connection_issue",
		"priority": 20,
		"keywords": ["database connection failed", "database connection timeout", "postgres", "mysql"],
		"confidence": 0.85,
		"suggested_actions": "Check database availability, network connectivity, and application connection settings.",
		"commands_to_check": [
			"systemctl status postgresql",
			"ss -tulpn",
			"journalctl -u postgresql -xe",
		],
	},
	{
		"category": "tls_certificate_issue",
		"priority": 30,
		"keywords": ["certificate expired", "tls", "ssl", "x509"],
		"confidence": 0.85,
		"suggested_actions": "Check certificate validity, expiration date, and service TLS configuration.",
		"commands_to_check": [
			"openssl x509 -in cert.pem -noout -dates",
			"openssl s_client -connect HOST:443",
			"systemctl reload nginx",
		],
	},
	{
		"category": "disk_usage_full",
		"priority": 40,
		"keywords": ["no space left", "disk full", "filesystem full"],
		"confidence": 0.90,
		"suggested_actions": "Check disk usage and clean up old logs, caches, or unused files.",
		"commands_to_check": [
			"df -h",
			"du -sh /var/log/*",
			"journalctl --disk-usage",
		],
	},
	{
		"category": "permission_denied",
		"priority": 50,
		"keywords": ["permission denied", "access denied"],
		"confidence": 0.80,
		"suggested_actions": "Check file ownership, permissions, and the user running the service.",
		"commands_to_check": [
			"ls -l",
			"id",
			"systemctl status SERVICE_NAME",
		],
	},
	{
		"category": "port_already_in_use",
		"priority": 60,
		"keywords": ["address already in use", "port already in use"],
		"confidence": 0.85,
		"suggested_actions": "Find which process is already listening on the port.",
		"commands_to_check": [
			"ss -tulpn",
			"lsof -i :PORT",
			"systemctl status SERVICE_NAME",
		],
	},
	{
		"category": "dns_lookup_failure",
		"priority": 70,
		"keywords": ["could not resolve", "name resolution", "dns lookup", "temporary failure in name resolution"],
		"confidence": 0.80,
		"suggested_actions": "Check DNS resolution, resolver configuration, and network connectivity.",
		"commands_to_check": [
			"dig example.com",
			"nslookup example.com",
			"cat /etc/resolv.conf",
		],
	},
	{
		"category": "systemd_service_failed",
		"priority": 80,
		"keywords": [".service failed", "failed to start", "unit failed"],
		"confidence": 0.85,
		"suggested_actions": "Check the systemd unit status and recent journal logs.",
		"commands_to_check": [
			"systemctl status SERVICE_NAME",
			"journalctl -u SERVICE_NAME -xe",
		],
	},
]

def seed_severity_rules(connection):
	cursor = connection.cursor()

	cursor.execute("SELECT COUNT(*) AS count FROM severity_levels")
	if cursor.fetchone()["count"] > 0:
		return

	for name, priority, keywords in DEFAULT_SEVERITY_RULES:
		cursor.execute(
			"""
			INSERT INTO severity_levels (name, priority, enabled)
			VALUES (?, ?, 1)
			""",
			(name, priority),
		)

		severity_id = cursor.lastrowid

		for keyword in keywords:
			cursor.execute(
				"""
				INSERT INTO severity_keywords (severity_id, keyword)
				VALUES (?, ?)
				""",
				(severity_id, keyword),
			)

	connection.commit()


def seed_component_rules(connection):
	cursor = connection.cursor()

	cursor.execute("SELECT COUNT(*) AS count FROM component_rules")
	if cursor.fetchone()["count"] > 0:
		return

	for component, priority, keywords in DEFAULT_COMPONENT_RULES:
		cursor.execute(
			"""
			INSERT INTO component_rules (component, priority, enabled)
			VALUES (?, ?, 1)
			""",
			(component, priority),
		)

		component_rule_id = cursor.lastrowid

		for keyword in keywords:
			cursor.execute(
				"""
				INSERT INTO component_keywords (component_rule_id, keyword)
				VALUES (?, ?)
				""",
				(component_rule_id, keyword),
			)

	connection.commit()


def seed_triage_rules(connection):
	cursor = connection.cursor()

	cursor.execute("SELECT COUNT(*) AS count FROM triage_rules")
	if cursor.fetchone()["count"] > 0:
		return

	for rule in DEFAULT_TRIAGE_RULES:
		cursor.execute(
			"""
			INSERT INTO triage_rules (
				category,
				confidence,
				suggested_actions,
				priority,
				enabled
			)
			VALUES (?, ?, ?, ?, 1)
			""",
			(
				rule["category"],
				rule["confidence"],
				rule["suggested_actions"],
				rule["priority"],
			),
		)

		triage_rule_id = cursor.lastrowid

		for keyword in rule["keywords"]:
			cursor.execute(
				"""
				INSERT INTO triage_keywords (triage_rule_id, keyword)
				VALUES (?, ?)
				""",
				(triage_rule_id, keyword),
			)

		for index, command in enumerate(rule["commands_to_check"]):
			cursor.execute(
				"""
				INSERT INTO triage_commands (
					triage_rule_id,
					command,
					command_order
				)
				VALUES (?, ?, ?)
				""",
				(triage_rule_id, command, index),
			)

	connection.commit()


def seed_default_rules(connection):
	seed_severity_rules(connection)
	seed_component_rules(connection)
	seed_triage_rules(connection)