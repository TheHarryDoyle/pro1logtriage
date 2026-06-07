import json

from db.database import get_db_connection
from models.log_models import AnalyzeLogsResponse

def save_log_analysis(raw_log: str, result: AnalyzeLogsResponse) -> int:
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
		INSERT INTO log_analyses (
			raw_log,
			line_count,
			timestamp,
			severity,
			component,
			category,
			confidence,
			suggested_actions,
			commands_to_check,
			analyzed_lines
		)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		""", (
            raw_log,
            result.line_count,
            result.timestamp,
            result.severity,
            result.component,
            result.category,
            result.confidence,
            result.suggested_actions,
            json.dumps(result.commands_to_check),
            json.dumps(result.analyzed_lines)
        )
    )
    connection.commit()
    connection.close()
    return cursor.lastrowid

def get_recent_log_analyses(limit: int = 10):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
		"""
		SELECT
			id,
			raw_log,
			line_count,
			timestamp,
			severity,
			component,
			category,
			confidence,
			suggested_actions,
			commands_to_check,
			analyzed_lines,
			created_at
		FROM log_analyses
		ORDER BY id DESC
		LIMIT ?
		""",
		(limit,),
	)
    rows = cursor.fetchall()
    connection.close()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "raw_log": row["raw_log"],
            "line_count": row["line_count"],
            "timestamp": row["timestamp"],
            "severity": row["severity"],
            "component": row["component"],
            "category": row["category"],
            "confidence": row["confidence"],
            "suggested_actions": (row["suggested_actions"]),
            "commands_to_check": json.loads(row["commands_to_check"]),
            "analyzed_lines": json.loads(row["analyzed_lines"]),
            "created_at": row["created_at"]
        })
        
    return results
