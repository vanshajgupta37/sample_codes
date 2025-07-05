import bisect

class LoyaltyHotspot:
    """
    Solves the Dynamic Loyalty Hotspot problem.

    Problem Description:
    Imagine you're building a feature for a social network. In this network,
    people have friends, and those friendships connect them into groups (you're
    in the same group as your friends, your friends' friends, and so on).
    Every person has a "loyalty score." Your task is to build a system that
    can handle two things very quickly:

    1. update_loyalty: The loyalty score of any person can change at any time.
    2. query_max_loyalty: For any person, you need to find the absolute highest
       loyalty score within their entire friend group.

    Core Challenge:
    The main difficulty is handling updates efficiently. If the person with the
    current highest score gets their loyalty *lowered*, the system must instantly
    find the *new* highest score among everyone else in their group without a

    slow, manual search. This solution uses a Disjoint Set Union (DSU) data
    structure to manage friend groups, where each group maintains a sorted list
    of its members' scores to make finding the maximum instantaneous.
    """

    def __init__(self, n, friendships, initial_loyalties):
        """
        Initializes the Loyalty Hotspot system.

        This sets up the internal structures for tracking friend groups and scores.
        It processes the initial friendships to form the starting components.

        Args:
            n (int): The total number of people in the network, numbered 0 to n-1.
            friendships (list[tuple[int, int]]): A list of pairs, where each
                pair represents a friendship between two people.
            initial_loyalties (list[int]): A list containing the starting loyalty
                score for each person, indexed by their ID.
        """
        # DSU parent pointers
        self._parent = list(range(n))
        # Store the current loyalty score of each person
        self._loyalties = list(initial_loyalties)
        # For each group, store a sorted list of its scores
        self._scores_in_component = {i: [initial_loyalties[i]] for i in range(n)}

        for p1, p2 in friendships:
            self._union(p1, p2)

    def _find(self, i):
        """Finds the representative of the group person 'i' is in (with path compression)."""
        if self._parent[i] == i:
            return i
        self._parent[i] = self._find(self._parent[i])
        return self._parent[i]

    def _union(self, i, j):
        """Merges the friend groups of person 'i' and person 'j'."""
        root_i = self._find(i)
        root_j = self._find(j)

        if root_i != root_j:
            # Union by size: merge smaller group into larger one for efficiency.
            if len(self._scores_in_component[root_i]) < len(self._scores_in_component[root_j]):
                root_i, root_j = root_j, root_i

            self._parent[root_j] = root_i
            self._scores_in_component[root_i].extend(self._scores_in_component[root_j])
            self._scores_in_component[root_i].sort()
            del self._scores_in_component[root_j]

    def update_loyalty(self, person, new_loyalty):
        """
        Updates a person's loyalty and adjusts the group's score list.

        This operation finds the person's group, updates their individual score,
        and then efficiently removes their old score and inserts the new score
        into the group's sorted list of scores.

        Args:
            person (int): The ID of the person whose score is to be updated.
            new_loyalty (int): The new loyalty score for the person.

        Raises:
            ValueError: If the person ID is invalid (out of bounds).
        """
        if not (0 <= person < len(self._parent)):
            raise ValueError("This person doesn't exist in the network.")

        component_root = self._find(person)
        old_loyalty = self._loyalties[person]
        self._loyalties[person] = new_loyalty

        component_scores = self._scores_in_component[component_root]
        component_scores.remove(old_loyalty)
        bisect.insort(component_scores, new_loyalty)

    def query_max_loyalty(self, person):
        """
        Finds the highest loyalty score in the person's entire friend group.

        Args:
            person (int): The ID of the person to query.

        Returns:
            int: The maximum loyalty score found within the person's connected
                 friend group. Returns -1 if the group somehow has no scores.

        Raises:
            ValueError: If the person ID is invalid (out of bounds).
        """
        if not (0 <= person < len(self._parent)):
            raise ValueError("This person doesn't exist in the network.")

        component_root = self._find(person)
        component_scores = self._scores_in_component[component_root]

        if not component_scores:
            return -1

        return component_scores[-1]

# =================
#  TESTS
# =================
def run_loyalty_hotspot_tests():
    # Test 1: Normal Case - Basic queries
    n = 5
    friendships = [(0, 1), (1, 2)]
    loyalties = [10, 100, 50, 5, 20]
    lh = LoyaltyHotspot(n, friendships, loyalties)
    assert lh.query_max_loyalty(0) == 100
    assert lh.query_max_loyalty(3) == 5

    # Test 2: Normal Case - An update increases the max loyalty
    lh.update_loyalty(0, 200)
    assert lh.query_max_loyalty(1) == 200

    # Test 3: Edge Case - Update decreases the max holder
    # The system must find the new highest score (100) after the old max (200) is lowered.
    lh.update_loyalty(0, 1)
    assert lh.query_max_loyalty(2) == 100

    # Test 4: Long Case - Multiple components and a merge
    n_long = 6
    friendships_long = [(0, 1), (3, 4), (4, 5)]
    loyalties_long = [10, 20, 99, 50, 60, 55]
    lh_long = LoyaltyHotspot(n_long, friendships_long, loyalties_long)
    lh_long._union(1, 2)
    assert lh_long.query_max_loyalty(0) == 99

    # Test 5: Edge Case - A person with no friends (isolated component)
    n_iso = 3
    friendships_iso = []
    loyalties_iso = [10, 20, 30]
    lh_iso = LoyaltyHotspot(n_iso, friendships_iso, loyalties_iso)
    assert lh_iso.query_max_loyalty(0) == 10
    lh_iso.update_loyalty(0, 5)
    assert lh_iso.query_max_loyalty(0) == 5

    # Test 6: Edge Case - All members have the same score
    n_same = 4
    friendships_same = [(0, 1), (2, 3), (1, 2)] # All connected
    loyalties_same = [50, 50, 50, 50]
    lh_same = LoyaltyHotspot(n_same, friendships_same, loyalties_same)
    assert lh_same.query_max_loyalty(0) == 50
    lh_same.update_loyalty(1, 40) # Lower one score
    assert lh_same.query_max_loyalty(2) == 50 # Max should still be 50
    lh_same.update_loyalty(3, 90) # Raise one score
    assert lh_same.query_max_loyalty(0) == 90 # Max should now be 90

    # Test 7: Complex Merge Case
    # Two separate groups with their own max scores are merged.
    n_merge = 6
    friendships_merge = [(0, 1), (3, 4)] # Group {0,1} and {3,4}
    loyalties_merge = [10, 100, 20, 200, 50, 30] # Maxes are 100 and 200
    lh_merge = LoyaltyHotspot(n_merge, friendships_merge, loyalties_merge)
    lh_merge._union(1, 3) # Merge the two groups
    # The new max for the combined group {0,1,3,4} must be 200.
    assert lh_merge.query_max_loyalty(0) == 200
    assert lh_merge.query_max_loyalty(4) == 200

    print("✅ All 7 LoyaltyHotspot tests passed!")


if __name__ == "__main__":
    run_loyalty_hotspot_tests()