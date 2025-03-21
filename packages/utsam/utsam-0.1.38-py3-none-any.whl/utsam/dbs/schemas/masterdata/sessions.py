from dataclasses import dataclass

@dataclass
class PgSessionsTable:
    name: str = "sessions"
    session_id: str = 'session_id'
    session_year: str = 'session_year'