import json
import re
from typing import Dict, List


class RequirementCheckerAgent:
    """
    Agent 3: Checks whether all requirements from the Planner
    have been implemented by the Coder.

    Responsibilities:
    - Compare planner requirements vs generated code
    - Detect missing features/files/functions
    - Return structured JSON ONLY
    """

    def run(self, plan: Dict, code: Dict) -> Dict:
        """
        plan: output of Agent 1
        code: output of Agent 2 (parsed JSON)
        """

        requirements = self._extract_requirements(plan)

            # ---- NORMALIZE CODE INPUT ----
        if hasattr(code, "dict"):
            code = code.dict()

        if not isinstance(code, dict):
            raise TypeError("Agent 3 expected code as dict or Pydantic model")

        files = code.get("files", {})

        missing = []

        for req in requirements:
            if not self._requirement_implemented(req, files):
                missing.append(req)

        if missing:
            return {
                "complete": False,
                "missing_requirements": missing,
                "feedback": self._build_feedback(missing)
            }

        return {"complete": True}

    # ----------------- Helpers -----------------

    def _extract_requirements(self, plan: Dict) -> List[str]:
        """
        Normalize requirements from planner output.
        """
        reqs = []

        if "requirements" in plan:
            reqs.extend(plan["requirements"])

        if "features" in plan:
            reqs.extend(plan["features"])

        if "success_criteria" in plan:
            reqs.extend(plan["success_criteria"])

        return [r.lower() for r in reqs]

    def _requirement_implemented(self, requirement: str, files: Dict) -> bool:
        """
        Heuristic check:
        - Keyword presence in any file
        - Function/class names
        """

        keywords = self._keywords_from_requirement(requirement)

        for filename, content in files.items():
            content_lower = content.lower()
            if any(k in content_lower for k in keywords):
                return True

        return False

    def _keywords_from_requirement(self, requirement: str) -> List[str]:
        """
        Extract meaningful keywords from a requirement sentence.
        """
        tokens = re.findall(r"[a-zA-Z_]+", requirement)
        stopwords = {
            "the", "a", "an", "and", "or", "to", "can", "user",
            "should", "be", "with", "for", "of"
        }
        return [t for t in tokens if t not in stopwords]

    def _build_feedback(self, missing: List[str]) -> str:
        """
        Human-readable feedback for Agent 2.
        """
        lines = ["The following requirements are not implemented:"]
        for req in missing:
            lines.append(f"- {req}")
        return "\n".join(lines)
