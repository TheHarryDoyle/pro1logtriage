from repositories.rule_repository import get_triage_rules


def triage_log(raw_log: str) -> dict:
	text = raw_log.lower()
	triage_rules = get_triage_rules()

	for rule in triage_rules:
		for keyword in rule["keywords"]:
			if keyword.lower() in text:
				return {
					"category": rule["category"],
					"confidence": rule["confidence"],
					"suggested_actions": rule["suggested_actions"],
					"commands_to_check": rule["commands_to_check"],
				}

	return {
		"category": "unknown",
		"confidence": 0.30,
		"suggested_actions": "No specific rule matched. Review the full log context manually.",
		"commands_to_check": [
			"journalctl -xe",
			"dmesg | tail",
			"systemctl status SERVICE_NAME",
		],
	}