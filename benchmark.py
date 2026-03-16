import subprocess
import sys

NUM_GAMES = 5

# Change these strings if your main.py prints different win messages
PLAYER_1_MARKERS = [
    "Winner: 0",
]
PLAYER_2_MARKERS = [
    "Winner: 1",
]


def contains_any(text: str, markers: list[str]) -> bool:
    text_lower = text.lower()
    return any(marker.lower() in text_lower for marker in markers)


def run_one_game() -> str:
    completed = subprocess.run(
        [sys.executable, "main.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    output = (completed.stdout or "") + "\n" + (completed.stderr or "")
    return output.strip()


def main() -> None:
    p1_wins = 0
    p2_wins = 0
    unknown = 0

    for i in range(1, NUM_GAMES + 1):
        print(f"Running game {i}/{NUM_GAMES}")
        try:
            output = run_one_game()

            if contains_any(output, PLAYER_1_MARKERS):
                p1_wins += 1
                print(f"Game {i}: Player 1 win")
            elif contains_any(output, PLAYER_2_MARKERS):
                p2_wins += 1
                print(f"Game {i}: Player 2 win")
            else:
                unknown += 1
                print(f"Game {i}: Could not determine winner")
                print(output)
                print("-" * 50)

        except subprocess.TimeoutExpired:
            unknown += 1
            print(f"Game {i}: Timed out")
            print("-" * 50)

    print("\n=== Benchmark Results ===")
    print(f"Total games: {NUM_GAMES}")
    print(f"Player 1 wins: {p1_wins}")
    print(f"Player 2 wins: {p2_wins}")
    print(f"Unknown / failed: {unknown}")


if __name__ == "__main__":
    main()