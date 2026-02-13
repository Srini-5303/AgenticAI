from agents.planner.agent import PlannerAgent
from agents.coder.agent import CoderAgent
from agents.checker.agent import RequirementCheckerAgent


def main():
    print("=== Agentic Builder (OSS) ===\n")

    user_input = input("Describe what you want to build:\n> ")

    planner = PlannerAgent()
    coder = CoderAgent()
    checker = RequirementCheckerAgent()

    # ---------- Agent 1 ----------
    plan = planner.run(user_input)

    # ---------- Agent 2 ↔ Agent 3 Loop ----------
    max_iters = 3
    for i in range(max_iters):
        print(f"\n--- Coding Iteration {i+1} ---")

        code = coder.run(plan)
        check = checker.run(plan, code)

        if check.get("complete"):
            print("All requirements implemented.")
            break

        print("Missing requirements:")
        for r in check["missing_requirements"]:
            print(f" - {r}")

        # Feed missing requirements back to Agent 2
        plan["missing_requirements"] = check["missing_requirements"]

    else:
        raise RuntimeError("Failed to satisfy requirements after retries.")
    
    print("\n--- GENERATED PLAN ---")
    print(json.dumps(plan.model_dump(), indent=2))

    print("\n--- GENERATED FILES ---")
    for filename, content in code.files.items():
        print(f"\n# {filename}\n")
        print(content)


    print("\nCode passed requirement checks.")
    print("Proceeding to debugging phase (Agent 4 next).")

if __name__ == "__main__":
    main()
