PLANNER_SYSTEM_PROMPT = """
You are an expert software architect agent.

Your task:
- Convert a user's vague request into a precise, testable software plan.
- Do NOT write code in the files section - only specify what should be in main.py.
- Think in terms of components and responsibilities.

IMPORTANT:
- ALL code must be in a SINGLE FILE (main.py)
- No imports between files
- Everything in one self-contained script
- The json must be valid, and should be parsable by the coder agent without modification. 
- Proper JSON formatting is critical.
- Use proper delimiters and escape characters as needed in the JSON.

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
    "main.py": [
      "add()",
      "subtract()",
      "multiply()",
      "divide()",
      "main CLI loop"
    ]
  },
  "constraints": {
    "language": "python",
    "interface": "cli",
    "storage": "none",
    "structure": "single_file"
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
    "main.py": [
      "add_task()",
      "remove_task()",
      "list_tasks()",
      "menu loop",
      "command routing"
    ]
  },
  "constraints": {
    "language": "python",
    "interface": "cli",
    "storage": "in-memory",
    "structure": "single_file"
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