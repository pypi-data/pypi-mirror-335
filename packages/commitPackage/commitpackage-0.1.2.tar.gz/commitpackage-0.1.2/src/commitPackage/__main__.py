import argparse
from commitPackage.lazyCommit import (
    generate_commit_message, random_commit_message,
    git_blame_excuse, generate_haiku, add_commit_message, add_excuse, add_haiku
)
    

def main():
    # COMMAND LINE TESTING
    parser = argparse.ArgumentParser(
        description="LazyCommit: Generate commit messages easily!")

    parser.add_argument(
        "--style", type=str, help="Generate a commit message with a specific style (funny, serious)")
    parser.add_argument("--random", action="store_true",
                        help="Generate a completely random commit message")
    parser.add_argument("--blame", action="store_true",
                        help="Get a funny git blame excuse")
    parser.add_argument("--haiku", action="store_true",
                        help="Generate a Haiku-style commit message")
    parser.add_argument(
        "--addMessage", type=str, nargs=2, metavar=('style', 'message'),
        help="Add a commit message to a specific style. Requires style and message as arguments (e.g., --addMessage funny 'Fixed a typo')")
    parser.add_argument(
        "--addExcuse", type=str, metavar=('message'),
        help="Add a git excuse. Requires message as an arguments (e.g., --addExcuse 'The intern wrote this line')")
    parser.add_argument(
        "--addHaiku", type=str, metavar=('message'),
        help="Add a git haiku. Requires message as an arguments (e.g., --addHaiku 'Code flows like the stream, Errors hidden in the mist Hope this works for you.')")

    args = parser.parse_args()

    if args.addMessage:
        style, message = args.addMessage
        print(add_commit_message(style, message))
    elif args.addExcuse:
        message = args.addExcuse[0]
        print(add_excuse(message))
    elif args.addHaiku:
        message = args.addHaiku[0]
        print(add_haiku(message))
    elif args.style:
        print(generate_commit_message(args.style))
    elif args.random:
        print(random_commit_message())
    elif args.blame:
        print(git_blame_excuse())
    elif args.haiku:
        print(generate_haiku())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
