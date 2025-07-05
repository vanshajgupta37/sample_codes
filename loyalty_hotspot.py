from typing import List, Tuple, Any
import bisect


def process_loyalty_operations(n: int, initial_friendships: List[Tuple[int, int]],
                               initial_loyalties: List[int],
                               operations: List[Tuple[str, Any, Any]]) -> List[int]:
    """
    Manages loyalty scores within dynamic friend groups using DSU within a single function.
    Supports initial setup, union operations, loyalty updates, and queries for
    the maximum loyalty in any group based on a sequence of operations.

    Args:
        n: The total number of people.
        initial_friendships: A list of initial (person1, person2) tuples representing friendships.
        initial_loyalties: A list of initial loyalty scores for each person.
        operations: A list of tuples, each representing an operation:
            - ("union", person1_idx, person2_idx): Merges the groups of person1 and person2.
            - ("update", person_idx, new_loyalty_score): Updates the loyalty of a person.
            - ("query_max", person_idx, None): Queries the maximum loyalty in a person's group.

    Returns:
        A list of results for "query_max" operations in the order they appear.
    """

    # --- Internal state (formerly class attributes) ---
    _parent: List[int] = list(range(n))
    _loyalties: List[int] = list(initial_loyalties)
    _scores_in_component: dict = {i: [initial_loyalties[i]] for i in range(n)}
    query_results: List[int] = []

    # --- Helper functions (inlined within the main function) ---
    def _find(i: int) -> int:
        """Finds the representative of person 'i's group (path compression)."""
        if _parent[i] == i:
            return i
        _parent[i] = _find(_parent[i])  # Path compression
        return _parent[i]

    def _union(i: int, j: int) -> None:
        """Merges groups of person 'i' and person 'j' (union by size/rank not strictly implemented but implied by len check)."""
        root_i = _find(i)
        root_j = _find(j)

        if root_i != root_j:
            # Union by size heuristic: attach smaller tree to root of larger tree
            if len(_scores_in_component[root_i]) < len(_scores_in_component[root_j]):
                root_i, root_j = root_j, root_i

            _parent[root_j] = root_i
            # Merge sorted lists: extend and re-sort for simplicity,
            # for performance, could use a merge-like approach if keeping sorted
            _scores_in_component[root_i].extend(_scores_in_component[root_j])
            _scores_in_component[root_i].sort()  # Maintain sorted property
            del _scores_in_component[root_j]

    # --- Initial setup (from _init_) ---
    for p1, p2 in initial_friendships:
        _union(p1, p2)

    # --- Process operations ---
    for op_type, arg1, arg2 in operations:
        if op_type == "union":
            _union(arg1, arg2)
        elif op_type == "update":
            person = arg1
            new_loyalty = arg2

            component_root = _find(person)
            old_loyalty = _loyalties[person]
            _loyalties[person] = new_loyalty

            component_scores = _scores_in_component[component_root]
            # Remove old loyalty: find and remove the first occurrence
            # Note: if there are duplicate loyalty scores, this might remove the wrong one
            # if not careful. For this problem's constraints, assuming direct removal is fine.
            try:
                component_scores.remove(old_loyalty)
            except ValueError:
                # This could happen if old_loyalty was already updated or somehow missing.
                # For robustness, you might want to log this or handle it more gracefully.
                pass
            bisect.insort(component_scores, new_loyalty)
        elif op_type == "query_max":
            person = arg1

            component_root = _find(person)
            component_scores = _scores_in_component[component_root]
            query_results.append(component_scores[-1])  # Max is last element in sorted list

    return query_results


# ====================== TEST CASES ======================

def test_one():
    # Initial setup: 5 people, (0,1) and (1,2) friendships, loyalties
    # Operations: Query max for 0, Query max for 3
    results = process_loyalty_operations(
        5, [(0, 1), (1, 2)], [10, 100, 50, 5, 20],
        [
            ("query_max", 0, None),
            ("query_max", 3, None)
        ]
    )
    assert results == [100, 5]


def test_two():
    # Initial setup
    # Operations: Update 0 to 200, Query max for 1
    results = process_loyalty_operations(
        5, [(0, 1), (1, 2)], [10, 100, 50, 5, 20],
        [
            ("update", 0, 200),
            ("query_max", 1, None)
        ]
    )
    assert results == [200]


def test_three():
    # Initial setup
    # Operations: Update 0 to 200, Update 0 to 1, Query max for 2
    results = process_loyalty_operations(
        5, [(0, 1), (1, 2)], [10, 100, 50, 5, 20],
        [
            ("update", 0, 200),
            ("update", 0, 1),
            ("query_max", 2, None)
        ]
    )
    assert results == [100]


def test_four():
    # Initial setup
    # Operations: Union 1 and 2, Query max for 0
    results = process_loyalty_operations(
        6, [(0, 1), (3, 4), (4, 5)], [10, 20, 99, 50, 60, 55],
        [
            ("union", 1, 2),
            ("query_max", 0, None)
        ]
    )
    assert results == [99]


def test_five():
    # Initial setup
    # Operations: Query max for 0, Update 0 to 5, Query max for 0
    results = process_loyalty_operations(
        3, [], [10, 20, 30],
        [
            ("query_max", 0, None),
            ("update", 0, 5),
            ("query_max", 0, None)
        ]
    )
    assert results == [10, 5]


def test_six():
    # Initial setup
    # Operations: Query max 0, Update 1 to 40, Query max 2, Update 3 to 90, Query max 0
    results = process_loyalty_operations(
        4, [(0, 1), (2, 3), (1, 2)], [50, 50, 50, 50],
        [
            ("query_max", 0, None),
            ("update", 1, 40),
            ("query_max", 2, None),
            ("update", 3, 90),
            ("query_max", 0, None)
        ]
    )
    assert results == [50, 50, 90]


def test_seven():
    # Initial setup
    # Operations: Union 1 and 3, Query max 0, Query max 4
    results = process_loyalty_operations(
        6, [(0, 1), (3, 4)], [10, 100, 20, 200, 50, 30],
        [
            ("union", 1, 3),
            ("query_max", 0, None),
            ("query_max", 4, None)
        ]
    )
    assert results == [200, 200]