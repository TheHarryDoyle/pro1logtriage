TRIAGE_RULES = [
	{
		"category": "nginx_upstream_timeout",
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
		"keywords": [".service failed", "failed to start", "unit failed"],
		"confidence": 0.85,
		"suggested_actions": "Check the systemd unit status and recent journal logs.",
		"commands_to_check": [
			"systemctl status SERVICE_NAME",
			"journalctl -u SERVICE_NAME -xe",
		],
	},
]

def triage_log(raw_log: str) -> dict:
    text = raw_log.lower()

    for rule in TRIAGE_RULES:
        for kw in rule["keywords"]:
            if kw.lower() in text:
                return {
                    "category": rule["category"],
                    "confidence": rule["confidence"],
                    "suggested_actions": rule["suggested_actions"],
                    "commands_to_check": rule["commands_to_check"],
                }
    
    return {
        "category": "unknown",
        "confidence": 0.0,
        "suggested_actions": "No matching triage rule found.",
        "commands_to_check": [],
    }