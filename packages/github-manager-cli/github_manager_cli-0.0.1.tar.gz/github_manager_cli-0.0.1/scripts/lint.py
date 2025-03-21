#!/usr/bin/env python3
import os
import sys
from pylint import lint

def main():
    """Run pylint on the project."""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(current_dir, 'src')

    # Files to analyze
    python_files = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    # Configure pylint
    options = [
        '--rcfile=' + os.path.join(current_dir, '.pylintrc'),
        '--output-format=colorized',
    ]
    options.extend(python_files)

    # Run pylint
    print("Running Pylint...")
    print("Analyzing files:", *python_files, sep='\n- ')
    print("\nResults:")

    try:
        run = lint.Run(options, exit=False)
        score = run.linter.stats.global_note
        print(f"\nCode Quality Score: {score:.2f}/10")

        if score < 7:
            print("\nWarning: Code quality score is below 7.0")
            sys.exit(1)

    except Exception as e:
        print(f"Error running pylint: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
