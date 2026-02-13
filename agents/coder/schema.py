from pydantic import BaseModel
from typing import Dict


class CodeOutput(BaseModel):
    files: Dict[str, str]
