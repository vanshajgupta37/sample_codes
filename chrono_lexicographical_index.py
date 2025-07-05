from typing import List, Tuple, Optional
import bisect


def query_prefix_recent_timestamp(operations: List[Tuple[str, str, int]]) -> Optional[int]:
    """
    Performs a series of add_word operations and then a single
    query_prefix_recent_timestamp operation on the simulated data,
    with all logic directly contained within this function.

    The operations list should contain tuples where:
    - The first element is the operation type ("add" or "query_prefix").
    - For "add", the second element is the word (str) and the third is the timestamp (int).
    - For "query_prefix", the second element is the prefix (str) and the third is unused (can be None or 0).

    Example:
        >>> query_prefix_recent_timestamp([("add", "apple", 10), ("add", "apply", 20), ("query_prefix", "app", 0)])
        20
    """
    _time_sorted_list: List[Tuple[int, str]] = []
    _prefix_trie: dict = {}

    result = None  # Initialize result to store the output of the query_prefix operation

    for op_type, arg1, arg2 in operations:
        if op_type == "add":
            word = arg1
            timestamp = arg2

            bisect.insort(_time_sorted_list, (timestamp, word))

            node = _prefix_trie
            # Update root's latest for empty prefix queries
            current_latest_ts_root = node.get('_latest', (-1, ''))[0]
            if timestamp >= current_latest_ts_root:
                node['_latest'] = (timestamp, word)

            for char in word:
                if char not in node:
                    node[char] = {}
                node = node[char]
                current_latest_ts = node.get('_latest', (-1, ''))[0]
                if timestamp >= current_latest_ts:
                    node['_latest'] = (timestamp, word)
            node['_end'] = True

        elif op_type == "query_prefix":
            prefix = arg1

            node = _prefix_trie
            for char in prefix:
                if char not in node:
                    result = None  # Set result to None if prefix not found
                    break  # Exit the loop early
                node = node[char]
            else:  # This else block executes if the for loop completes without a break
                if '_latest' in node:
                    result = node['_latest'][0]
                else:
                    result = None  # Set result to None if _latest not found at the end of prefix
            # Assuming only one "query_prefix" operation at the end for the final result
            # If multiple queries are expected, this would need to return a list of results
    return result


# ====================== TEST CASES (remain the same as they call the single function) ======================

def test_one():
    # This test case cannot be directly replicated as it calls query_time_range_lex_sort,
    # which is not included in the single function.
    pass


def test_two():
    # To test individual query_prefix_recent_timestamp calls, we need to restructure
    # the operations list for each assertion.
    assert query_prefix_recent_timestamp([
        ("add", "apple", 10),
        ("add", "apricot", 12),
        ("add", "banana", 15),
        ("add", "apply", 20),
        ("add", "bandana", 22),
        ("add", "cat", 30),
        ("query_prefix", "ap", 0)
    ]) == 20

    assert query_prefix_recent_timestamp([
        ("add", "apple", 10),
        ("add", "apricot", 12),
        ("add", "banana", 15),
        ("add", "apply", 20),
        ("add", "bandana", 22),
        ("add", "cat", 30),
        ("query_prefix", "ban", 0)
    ]) == 22


def test_three():
    # This test case cannot be directly replicated as it calls query_time_range_lex_sort.
    pass


def test_four():
    assert query_prefix_recent_timestamp([("query_prefix", "dog", 0)]) is None


def test_five():
    assert query_prefix_recent_timestamp([
        ("add", "apple", 10),
        ("add", "application", 25),
        ("query_prefix", "app", 0)
    ]) == 25


def test_six():
    # This test case cannot be directly replicated as it calls query_time_range_lex_sort.
    pass


def test_seven():
    assert query_prefix_recent_timestamp([
        ("add", "apple", 10),
        ("add", "applesauce", 26),
        ("query_prefix", "apple", 0)
    ]) == 26


def test_eight():
    assert query_prefix_recent_timestamp([
        ("add", "cat", 30),
        ("query_prefix", "", 0)
    ]) == 30

    assert query_prefix_recent_timestamp([
        ("add", "cat", 30),
        ("add", "zebra", 40),
        ("query_prefix", "", 0)
    ]) == 40