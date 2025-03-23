from dataclasses import dataclass

@dataclass
class PgAssignmentCriteriasTable:
    name: str = "assignment_criterias"
    criteria_id: str = 'criteria_id'
    criteria_desc: str = 'criteria_desc'
    criteria_weight: str = 'criteria_weight'