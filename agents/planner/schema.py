from pydantic import BaseModel
from typing import List, Dict


class PlannerOutput(BaseModel):
    project_name: str
    project_type: str

    features: List[str]

    components: Dict[str, List[str]]
    files: Dict[str, List[str]]

    constraints: Dict[str, str]

    success_criteria: List[str]
