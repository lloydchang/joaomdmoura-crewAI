#!/usr/bin/env python

# main.py

from tedxsdg.crew import run_crew

def run_tedxsdg_platform():
    print("Welcome to the TEDxSDG Platform!")
    print("\nDemonstrating the platform with two example ideas:")

    ideas = [
        ("Sam", "Launch an eco-friendly pet care initiative to promote responsible ownership and biodiversity"),
        ("Alex", "Develop a sustainable supply chain to combat hunger and reduce food waste")
    ]

    for protagonist, idea in ideas:
        print(f"\n\n{protagonist}'s Idea: {idea}")
        print("-" * 50)
        result = run_tedxsdg_crew(idea, protagonist)
        print("\nTEDxSDG Crew Execution Result:")
        print(result)
        print("=" * 50)

def run():
    """
    This function will be called by the 'crewai run' command.
    """
    run_crew()

if __name__ == "__main__":
    run()
