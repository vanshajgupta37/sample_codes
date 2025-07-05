from typing import List, Tuple
import bisect

class LoyaltyHotspot:
    """
    Manages loyalty scores within dynamic friend groups using DSU.
    Supports efficient updates and queries for the maximum loyalty in any group.
    """

    def __init__(self, n: int, friendships: List[Tuple[int, int]], initial_loyalties: List[int]):
        """
        Initializes the system with people, friendships, and loyalty scores.
        """
        self._parent = list(range(n))
        self._loyalties = list(initial_loyalties)
        self._scores_in_component = {i: [initial_loyalties[i]] for i in range(n)}

        for p1, p2 in friendships:
            self._union(p1, p2)

    def _find(self, i: int) -> int:
        """Finds the representative of person 'i's group."""
        if self._parent[i] == i:
            return i
        self._parent[i] = self._find(self._parent[i])
        return self._parent[i]

    def _union(self, i: int, j: int) -> None:
        """Merges groups of person 'i' and person 'j'."""
        root_i = self._find(i)
        root_j = self._find(j)

        if root_i != root_j:
            if len(self._scores_in_component[root_i]) < len(self._scores_in_component[root_j]):
                root_i, root_j = root_j, root_i

            self._parent[root_j] = root_i
            self._scores_in_component[root_i].extend(self._scores_in_component[root_j])
            self._scores_in_component[root_i].sort()
            del self._scores_in_component[root_j]

    def update_loyalty(self, person: int, new_loyalty: int) -> None:
        """
        Updates a person's loyalty score and refreshes their group's max score.
        """
        component_root = self._find(person)
        old_loyalty = self._loyalties[person]
        self._loyalties[person] = new_loyalty

        component_scores = self._scores_in_component[component_root]
        component_scores.remove(old_loyalty)
        bisect.insort(component_scores, new_loyalty)

    def query_max_loyalty(self, person: int) -> int:
        """
        Returns the highest loyalty score in the person's friend group.
        """
        component_root = self._find(person)
        component_scores = self._scores_in_component[component_root]
        return component_scores[-1]

# ====================== TEST CASES ======================

def test_one():
    lh = LoyaltyHotspot(5, [(0, 1), (1, 2)], [10, 100, 50, 5, 20])
    assert lh.query_max_loyalty(0) == 100
    assert lh.query_max_loyalty(3) == 5

def test_two():
    lh = LoyaltyHotspot(5, [(0, 1), (1, 2)], [10, 100, 50, 5, 20])
    lh.update_loyalty(0, 200)
    assert lh.query_max_loyalty(1) == 200

def test_three():
    lh = LoyaltyHotspot(5, [(0, 1), (1, 2)], [10, 100, 50, 5, 20])
    lh.update_loyalty(0, 200)
    lh.update_loyalty(0, 1)
    assert lh.query_max_loyalty(2) == 100

def test_four():
    lh = LoyaltyHotspot(6, [(0, 1), (3, 4), (4, 5)], [10, 20, 99, 50, 60, 55])
    lh._union(1, 2)
    assert lh.query_max_loyalty(0) == 99

def test_five():
    lh = LoyaltyHotspot(3, [], [10, 20, 30])
    assert lh.query_max_loyalty(0) == 10
    lh.update_loyalty(0, 5)
    assert lh.query_max_loyalty(0) == 5

def test_six():
    lh = LoyaltyHotspot(4, [(0, 1), (2, 3), (1, 2)], [50, 50, 50, 50])
    assert lh.query_max_loyalty(0) == 50
    lh.update_loyalty(1, 40)
    assert lh.query_max_loyalty(2) == 50
    lh.update_loyalty(3, 90)
    assert lh.query_max_loyalty(0) == 90

def test_seven():
    lh = LoyaltyHotspot(6, [(0, 1), (3, 4)], [10, 100, 20, 200, 50, 30])
    lh._union(1, 3)
    assert lh.query_max_loyalty(0) == 200
    assert lh.query_max_loyalty(4) == 200
