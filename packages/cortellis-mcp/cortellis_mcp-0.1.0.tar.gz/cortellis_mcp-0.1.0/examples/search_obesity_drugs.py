"""
Example script demonstrating how to search for obesity drugs in different phases.
"""
from cortellis_mcp import search_drugs

def main():
    # Search for Phase 3 obesity drugs
    phase3_results = search_drugs(
        indication="obesity",
        phase="C3"  # Phase 3 Clinical
    )
    print("\nPhase 3 Obesity Drugs:")
    print(phase3_results)

    # Search for launched obesity drugs
    launched_results = search_drugs(
        indication="obesity",
        phase="L"  # Launched
    )
    print("\nLaunched Obesity Drugs:")
    print(launched_results)

    # Search for specific company's obesity drugs
    company_results = search_drugs(
        company="Novo Nordisk",
        indication="obesity"
    )
    print("\nNovo Nordisk Obesity Drugs:")
    print(company_results)

if __name__ == "__main__":
    main() 