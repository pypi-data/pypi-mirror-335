import sys
import argparse


def main(repo, task_name, verbose=False):
    print(f"Running {task_name} with repository: {repo}")
    if verbose:
        print("Verbose mode is enabled")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run GI-2025 Task 1 (VQA)')
    parser.add_argument('repo2', type=str, help='Repository path')
    parser.add_argument('task_name2', type=str, help='Name of the task')
    parser.add_argument('--verbose2', action='store_true',
                        help='Enable verbose mode')

    args = parser.parse_args()
    main(args.repo2, args.task_name2, args.verbose2)
