#!/usr/bin/env python
import os
import sys
import warnings
from datetime import datetime

from crew import FactChecker
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }

    try:
        FactChecker().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"❌ An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        FactChecker().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"❌ An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        FactChecker().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"❌ An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and return the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        FactChecker().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"❌ An error occurred while testing the crew: {e}")

# Optional: call one of them directly if needed
if __name__ == "__main__":
    run()  # or train(), test(), replay() depending on use case
