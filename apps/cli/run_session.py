import argparse
from core.db import init_db
from core.orchestrator import start_session

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contest-id", type=int, required=True, help="Contest ID (e.g. 2072)")
    parser.add_argument("--letter", type=str, required=True, help="Problem letter (e.g. F)")
    parser.add_argument("--attempts", type=int, default=3, help="Maximum attempts")
    args = parser.parse_args()
    init_db()
    sid = start_session(args.contest_id, args.letter, args.attempts)
    print("Session:", sid)

if __name__ == "__main__":
    main()
