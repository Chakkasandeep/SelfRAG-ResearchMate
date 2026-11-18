import asyncio
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from guardrails.rails import check_output


def main() -> None:
    fabricated = (
        "A fabricated 94.6% hallucination-free clinical benefit is guaranteed "
        "and certainly proven by no source."
    )
    result = asyncio.run(check_output(fabricated, [], []))
    print("INPUT -> FABRICATED CLAIM")
    print("VERDICT -> " + result.action.upper())
    if result.action == "rewrite":
        print("REWRITTEN -> " + (result.output or ""))
    else:
        print("WITHHELD -> " + result.reason)


if __name__ == "__main__":
    main()
