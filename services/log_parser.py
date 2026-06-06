import re

SEVERITY_RULES = [
	("EMERGENCY", ["EMERGENCY", "EMERG", "PANIC", "<0>"]),
	("ALERT", ["ALERT", "<1>"]),
	("CRITICAL", ["CRITICAL", "CRIT", "<2>"]),
	("ERROR", ["ERROR", "ERR", "FAILED", "FAILURE", "<3>"]),
	("WARNING", ["WARNING", "WARN", "<4>"]),
	("NOTICE", ["NOTICE", "<5>"]),
	("INFO", ["INFO", "INFORMATIONAL", "<6>"]),
	("DEBUG", ["DEBUG", "DBG", "<7>"]),
]

COMPONENT_RULES = [
	("nginx", ["nginx", "upstream", "502", "504"]),
	("systemd", ["systemd", ".service", "failed to start"]),
	("database", ["database", "postgres", "postgresql", "mysql", "connection failed"]),
	("tls", ["certificate", "tls", "ssl", "x509"]),
	("dns", ["dns", "lookup", "resolve", "could not resolve", "name resolution"]),
	("disk", ["disk", "no space left", "filesystem", "volume full"]),
	("permissions", ["permission denied", "access denied"]),
	("network", ["port", "address already in use", "connection refused", "timeout"]),
]


def detect_severity ( raw_log: str) -> str:
    text = raw_log.upper()

    for severity,keywords in SEVERITY_RULES:
        for kw in keywords:
            if kw.upper() in text:
                return severity
            
    return "UNKNOWN"

def detect_component ( raw_log: str) -> str:
    text = raw_log.lower()

    for component,keywords in COMPONENT_RULES:
        for kw in keywords:
            if kw.lower() in text:
                return component
            
    return "unknown"

def detect_timestamp ( raw_log: str) ->str | None:
    # Common timestamp patterns
    patterns = [
        r'\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\b',  # ISO 8601 UTC
        r'\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b',   # Common log format
        r'\b\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\b',   # Alternative format
        r'\b[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\b' # Syslog format
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
        "analyzed_lines": lines
    }