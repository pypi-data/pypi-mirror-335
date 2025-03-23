from dataclasses import dataclass

@dataclass
class PgAssignmentSubcriteriasTable:
    name: str = "assignment_subcriterias"
    subcriteria_id: str = 'subcriteria_id'
    subcriteria_name: str = 'subcriteria_name'
    subcriteria_desc: str = 'subcriteria_desc'
    subcriteria_weight: str = 'subcriteria_weight'