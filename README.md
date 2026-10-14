# Chess Puzzle Experiment for Physiological Recording

A Pygame experiment comparing easy and hard problem solving. The participant solves
mate-in-1 (easy) and mate-in-3 (hard) chess puzzles while physiological signals
(EDA, PPG) are recorded. The aim is to identify differences in these signals between
the two conditions.

## Puzzles

Puzzles come from the Lichess puzzle database (lichess.org). Mate-in-1 puzzles are
rated 800–1000 and mate-in-3 puzzles 1200–1400, so the two conditions do not overlap
in difficulty. Only puzzles with a single correct mating move were kept.

## Design

- One session of 10 blocks, 15 puzzles per block (150 trials).
- Each block has three parts of 5 puzzles: mate1–mate3–mate1 in odd blocks,
  mate3–mate1–mate3 in even blocks (counterbalanced).
- Puzzles are selected randomly with fixed seeds, so every run is reproducible.
  No puzzle is repeated.
- Each trial: cue "Mate in 1" / "Mate in 3" (500 ms) → puzzle until solved →
  feedback "Correct" / "Wrong" (500 ms) → blank screen (500 ms).
- In mate-in-3 puzzles the participant also plays the opponent's replies.

## Requirements

- macOS (pieces use the system font Apple Symbols)
- Python 3 with pygame, python-chess and pandas:

      pip install pygame chess pandas

## Running

    cd ~/chess_puzzles
    python board.py

SPACE continues from instruction screens, ESC stops the session.

## Files

| File | Purpose |
|---|---|
| `board.py` | The experiment: plans the session, runs all blocks, writes the log. |
| `pool_mate1.csv` | Puzzle library for the mate-in-1 condition (171,579 puzzles). |
| `pool_mate3.csv` | Puzzle library for the mate-in-3 condition (22,321 puzzles). |
| `plan_<time>.csv` | The 150 puzzles of a run, in order. Written at start. |
| `log_<time>.csv` | One row per trial: moves, correctness, reaction times, clock times. |
| `aborted_<time>.csv` | Same as the log, if the session was stopped early. |

## Author
Anh To-Lefebvre
Contact: contact@anhlefebvre.fr
If you use this experiment or its code in your research, please give credit.

## License

The code is free to use, change, and share, as long as you give credit
(see the LICENSE file).

## Acknowledgements

- Puzzles: Lichess puzzle database (lichess.org), released under CC0.
- Libraries: pygame, python-chess, pandas.
