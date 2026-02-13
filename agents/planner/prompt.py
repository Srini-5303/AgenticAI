PLANNER_SYSTEM_PROMPT = """
You are an expert software architect agent.

Your task:
- Convert a user's vague request into a precise, testable software plan.
- Do NOT write code.
- Think in terms of components, files, and responsibilities.

Rules:
- Output must be VALID JSON.
- Follow the exact schema.
- Be minimal but complete.
- No explanations.
"""

PLANNER_FEW_SHOTS = [
    {
        "user": "Create a simple calculator app",
        "assistant": """
{
  "project_name": "calculator_app",
  "project_type": "cli_application",
  "features": [
    "add",
    "subtract",
    "multiply",
    "divide"
  ],
  "components": {
    "core_logic": [
      "addition function",
      "subtraction function",
      "multiplication function",
      "division function"
    ],
    "interface": [
      "CLI input handling",
      "result display"
    ]
  },
  "files": {
    "logic.py": [
      "add()",
      "subtract()",
      "multiply()",
      "divide()"
    ],
    "app.py": [
      "main CLI loop"
    ]
  },
  "constraints": {
    "language": "python",
    "interface": "cli",
    "storage": "none"
  },
  "success_criteria": [
    "User can input two numbers",
    "User can choose an operation",
    "Correct result is displayed"
  ]
}
"""
    },
    {
        "user": "Build a to-do list where users can add and remove tasks",
        "assistant": """
{
  "project_name": "todo_list",
  "project_type": "cli_application",
  "features": [
    "add_task",
    "remove_task",
    "list_tasks"
  ],
  "components": {
    "core_logic": [
      "task storage",
      "add task function",
      "remove task function",
      "list task function"
    ],
    "interface": [
      "CLI menu",
      "user input handling"
    ]
  },
  "files": {
    "logic.py": [
      "add_task()",
      "remove_task()",
      "list_tasks()"
    ],
    "app.py": [
      "menu loop",
      "command routing"
    ]
  },
  "constraints": {
    "language": "python",
    "interface": "cli",
    "storage": "in-memory"
  },
  "success_criteria": [
    "User can add a task",
    "User can remove a task",
    "User can view all tasks"
  ]
}
"""
    }
]
