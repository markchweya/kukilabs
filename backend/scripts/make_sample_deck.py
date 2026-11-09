"""Generate samples/search-algorithms.pptx, an ORIGINAL demo lecture.

Written for Kuki's demos so we never need to ship anyone else's slides. Free to
use under the repository's MIT license.

    python scripts/make_sample_deck.py
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation

SLIDES = [
    ("Search Algorithms", "Week 4 · How an agent finds a path from a start state to a goal",
     "Today: uninformed search (BFS, DFS) and informed search (greedy, A*)."),
    ("What is a search problem?",
     "Initial state: where the agent starts\nActions: what it can do in each state\n"
     "Transition model: the state that results from an action\nGoal test: are we done?\nPath cost: the price of a solution",
     "Every search algorithm in this lecture works on these five parts."),
    ("The frontier",
     "Frontier: the set of states we have discovered but not yet explored.\n"
     "Each step: remove a node from the frontier, test it, add its neighbours.\n"
     "Keep an explored set so we never expand the same state twice.",
     "Which node we remove first is the only difference between BFS and DFS."),
    ("Breadth-first search (BFS)",
     "BFS uses a queue: first in, first out.\nIt explores all nodes at depth 1, then depth 2, and so on.\n"
     "Complete: always finds a solution if one exists.\nOptimal when every step costs the same.",
     "Memory is the weakness: BFS stores every node on the current level."),
    ("Depth-first search (DFS)",
     "DFS uses a stack: last in, first out.\nIt follows one branch as deep as possible before backtracking.\n"
     "Uses little memory.\nNot optimal: the first solution found may be a long one.",
     "A common mistake is to think DFS finds the shortest path. It does not."),
    ("Informed search and heuristics",
     "Heuristic h(n): an estimate of the cost from node n to the goal.\n"
     "For example, straight-line distance is a heuristic for driving distance on a map.\n"
     "Greedy best-first search expands the node with the smallest h(n).",
     "Greedy search is fast but can be fooled by a heuristic that looks good locally."),
    ("A* search",
     "A* expands the node with the lowest f(n) = g(n) + h(n).\n"
     "g(n) is the cost of the path so far; h(n) is the estimated cost to the goal.\n"
     "A* is optimal if h(n) is admissible: it never overestimates the true cost.",
     "Students often forget g(n). Without it, A* becomes greedy search."),
    ("Comparing the algorithms",
     "BFS: complete, optimal for equal step costs, high memory.\n"
     "DFS: low memory, not optimal, can get lost in deep branches.\n"
     "Greedy: fast, not optimal.\nA*: optimal with an admissible heuristic.",
     "Exam tip: be ready to say WHY each property holds, not just list it."),
]


def main() -> None:
    deck = Presentation()
    for title, body, notes in SLIDES:
        slide = deck.slides.add_slide(deck.slide_layouts[1])
        slide.shapes.title.text = title
        slide.placeholders[1].text = body
        slide.notes_slide.notes_text_frame.text = notes
    out = Path(__file__).resolve().parents[2] / "samples" / "search-algorithms.pptx"
    out.parent.mkdir(exist_ok=True)
    deck.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
