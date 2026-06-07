from db.database import get_db_connection

from models.rule_models import (
	CreateSeverityRuleRequest,
	CreateComponentRuleRequest,
	CreateTriageRuleRequest,
)

def get_severity_rules() -> list[tuple[str, list[str]]]:
	connection = get_db_connection()
	cursor = connection.cursor()

	cursor.execute(
		"""
		SELECT id, name
		FROM severity_levels
		WHERE enabled = 1
		ORDER BY priority ASC
		"""
	)

	severity_rows = cursor.fetchall()
	rules = []

	for severity_row in severity_rows:
		cursor.execute(
			"""
			SELECT keyword
			FROM severity_keywords
			WHERE severity_id = ?
			ORDER BY id ASC
			""",
			(severity_row["id"],),
		)

		keyword_rows = cursor.fetchall()
		keywords = [row["keyword"] for row in keyword_rows]

		rules.append((severity_row["name"], keywords))

	connection.close()
	return rules


def get_component_rules() -> list[tuple[str, list[str]]]:
	connection = get_db_connection()
	cursor = connection.cursor()

	cursor.execute(
		"""
		SELECT id, component
		FROM component_rules
		WHERE enabled = 1
		ORDER BY priority ASC
		"""
	)

	component_rows = cursor.fetchall()
	rules = []

	for component_row in component_rows:
		cursor.execute(
			"""
			SELECT keyword
			FROM component_keywords
			WHERE component_rule_id = ?
			ORDER BY id ASC
			""",
			(component_row["id"],),
		)

		keyword_rows = cursor.fetchall()
		keywords = [row["keyword"] for row in keyword_rows]

		rules.append((component_row["component"], keywords))

	connection.close()
	return rules


def get_triage_rules() -> list[dict]:
	connection = get_db_connection()
	cursor = connection.cursor()

	cursor.execute(
		"""
		SELECT
			id,
			category,
			confidence,
			suggested_actions
		FROM triage_rules
		WHERE enabled = 1
		ORDER BY priority ASC
		"""
	)

	triage_rows = cursor.fetchall()
	rules = []

	for triage_row in triage_rows:
		cursor.execute(
			"""
			SELECT keyword
			FROM triage_keywords
			WHERE triage_rule_id = ?
			ORDER BY id ASC
			""",
			(triage_row["id"],),
		)

		keyword_rows = cursor.fetchall()
		keywords = [row["keyword"] for row in keyword_rows]

		cursor.execute(
			"""
			SELECT command
			FROM triage_commands
			WHERE triage_rule_id = ?
			ORDER BY command_order ASC
			""",
			(triage_row["id"],),
		)

		command_rows = cursor.fetchall()
		commands_to_check = [row["command"] for row in command_rows]

		rules.append(
			{
				"category": triage_row["category"],
				"keywords": keywords,
				"confidence": triage_row["confidence"],
				"suggested_actions": triage_row["suggested_actions"],
				"commands_to_check": commands_to_check,
			}
		)

	connection.close()
	return rules

def get_next_priority(table_name: str) -> int:
	connection = get_db_connection()
	cursor = connection.cursor()

	cursor.execute(f"SELECT COALESCE(MAX(priority), 0) + 10 AS next_priority FROM {table_name}")
	row = cursor.fetchone()

	connection.close()

	return row["next_priority"]


def add_severity_rule(request: CreateSeverityRuleRequest) -> dict:
	connection = get_db_connection()
	cursor = connection.cursor()

	priority = request.priority
	if priority is None:
		priority = get_next_priority("severity_levels")

	cursor.execute(
		"""
		INSERT INTO severity_levels (name, priority, enabled)
		VALUES (?, ?, ?)
		""",
		(
			request.name.upper(),
			priority,
			1 if request.enabled else 0,
		),
	)

	severity_id = cursor.lastrowid

	for keyword in request.keywords:
		cursor.execute(
			"""
			INSERT INTO severity_keywords (severity_id, keyword)
			VALUES (?, ?)
			""",
			(severity_id, keyword),
		)

	connection.commit()
	connection.close()

	return {
		"id": severity_id,
		"name": request.name.upper(),
		"priority": priority,
		"enabled": request.enabled,
		"keywords": request.keywords,
	}


def add_severity_keyword(severity_id: int, keyword: str) -> dict:
	connection = get_db_connection()
	cursor = connection.cursor()

	cursor.execute(
		"""
		INSERT INTO severity_keywords (severity_id, keyword)
		VALUES (?, ?)
		""",
		(severity_id, keyword),
	)

	connection.commit()
	new_id = cursor.lastrowid
	connection.close()

	return {
		"id": new_id,
		"severity_id": severity_id,
		"keyword": keyword,
	}


def add_component_rule(request: CreateComponentRuleRequest) -> dict:
	connection = get_db_connection()
	cursor = connection.cursor()

	priority = request.priority
	if priority is None:
		priority = get_next_priority("component_rules")

	cursor.execute(
		"""
		INSERT INTO component_rules (component, priority, enabled)
		VALUES (?, ?, ?)
		""",
		(
			request.component.lower(),
			priority,
			1 if request.enabled else 0,
		),
	)

	component_rule_id = cursor.lastrowid

	for keyword in request.keywords:
		cursor.execute(
			"""
			INSERT INTO component_keywords (component_rule_id, keyword)
			VALUES (?, ?)
			""",
			(component_rule_id, keyword),
		)

	connection.commit()
	connection.close()

	return {
		"id": component_rule_id,
		"component": request.component.lower(),
		"priority": priority,
		"enabled": request.enabled,
		"keywords": request.keywords,
	}


def add_component_keyword(component_rule_id: int, keyword: str) -> dict:
	connection = get_db_connection()
	cursor = connection.cursor()

	cursor.execute(
		"""
		INSERT INTO component_keywords (component_rule_id, keyword)
		VALUES (?, ?)
		""",
		(component_rule_id, keyword),
	)

	connection.commit()
	new_id = cursor.lastrowid
	connection.close()

	return {
		"id": new_id,
		"component_rule_id": component_rule_id,
		"keyword": keyword,
	}


def add_triage_rule(request: CreateTriageRuleRequest) -> dict:
	connection = get_db_connection()
	cursor = connection.cursor()

	priority = request.priority
	if priority is None:
		priority = get_next_priority("triage_rules")

	cursor.execute(
		"""
		INSERT INTO triage_rules (
			category,
			confidence,
			suggested_actions,
			priority,
			enabled
		)
		VALUES (?, ?, ?, ?, ?)
		""",
		(
			request.category,
			request.confidence,
			request.suggested_actions,
			priority,
			1 if request.enabled else 0,
		),
	)

	triage_rule_id = cursor.lastrowid

	for keyword in request.keywords:
		cursor.execute(
			"""
			INSERT INTO triage_keywords (triage_rule_id, keyword)
			VALUES (?, ?)
			""",
			(triage_rule_id, keyword),
		)

	for index, command in enumerate(request.commands_to_check):
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
	connection.close()

	return {
		"id": triage_rule_id,
		"category": request.category,
		"keywords": request.keywords,
		"confidence": request.confidence,
		"suggested_actions": request.suggested_actions,
		"commands_to_check": request.commands_to_check,
		"priority": priority,
		"enabled": request.enabled,
	}