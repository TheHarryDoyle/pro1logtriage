import re

from repositories.rule_repository import get_component_rules, get_severity_rules


def detect_severity(raw_log: str) -> str:
	text = raw_log.upper()
	severity_rules = get_severity_rules()

	for severity, keywords in severity_rules:
		for keyword in keywords:
			if keyword.upper() in text:
				return severity

	return "UNKNOWN"


def detect_component(raw_log: str) -> str:
	text = raw_log.lower()
	component_rules = get_component_rules()

	for component, keywords in component_rules:
		for keyword in keywords:
			if keyword.lower() in text:
				return component

	return "unknown"


def detect_timestamp(raw_log: str) -> str | None:
	patterns = [
		r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\b",
		r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b",
		r"\b\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\b",
		r"\b[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\b",
	]

	for pattern in patterns:
		match = re.search(pattern, raw_log)
		if match:
			return match.group(0)

	return None


def parse_log(raw_log: str) -> dict:
	lines = raw_log.splitlines()

	return {
		"line_count": len(lines),
		"timestamp": detect_timestamp(raw_log),
		"severity": detect_severity(raw_log),
		"component": detect_component(raw_log),
		"analyzed_lines": lines,
	}