import os
from agents.planner import PlannerAgent
from utils.pdf_utils import extract_text_from_pdf

def main():
    print("\n=== Planner Agent (Claude) ===\n")

    question = input("What do you want to build or plan?\n> ")

    use_pdf = input("\nDo you want to add a PDF context? (y/n): ").lower()
    context = ""

    if use_pdf == "y":
        pdf_path = input("Enter PDF file path: ").strip()

        if not os.path.exists(pdf_path):
            print("❌ PDF file not found.")
            return

        print("📄 Reading PDF...")
        context = extract_text_from_pdf(pdf_path)
        print("✅ PDF loaded.\n")

    planner = PlannerAgent()

    print("🧠 Planning...\n")
    output = planner.plan(question=question, context=context)

    print("\n========== PLAN OUTPUT ==========\n")
    print(output)
    print("\n=================================\n")

if __name__ == "__main__":
    main()
