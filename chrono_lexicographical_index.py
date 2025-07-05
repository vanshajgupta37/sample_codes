import bisect


class ChronoLexIndex:
    """
    Solves the Chrono-Lexicographical Index problem.

    Problem Description:
    You are building a system that logs events, where each event is a simple
    word and a timestamp. You need to be able to search these logs in two
    very different ways, and both searches must be super fast:

    1. Search by Time: Get all words logged within a specific time window,
       and return this list of words sorted alphabetically.
    2. Search by Prefix: Find the timestamp of the *most recently logged*
       word that starts with a certain prefix.

    Core Challenge:
    A data structure good for one task is usually bad for the other. A list
    sorted by time is great for the first query but bad for prefix searches.
    A Trie (a letter-based tree) is great for prefixes but bad for time ranges.
    The unique solution is to use both data structures simultaneously. Every
    new word updates both the time-sorted list and the Trie.
    """

    def __init__(self):
        """Initializes the dual data structures for indexing."""
        self._time_sorted_list = []
        self._prefix_trie = {}

    def add_word(self, word, timestamp):
        """
        Adds a word and its timestamp to both internal data structures.

        This method inserts the data into a time-sorted list for time-range
        queries and also into a Trie to enable efficient prefix searches.

        Args:
            word (str): The word to add to the index.
            timestamp (int): The timestamp associated with the word.
        """
        bisect.insort(self._time_sorted_list, (timestamp, word))

        # Update the latest entry for the root of the trie (for empty prefixes)
        root_latest_ts = self._prefix_trie.get('_latest', (-1, ''))[0]
        if timestamp >= root_latest_ts:
            self._prefix_trie['_latest'] = (timestamp, word)

        node = self._prefix_trie
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]

            current_latest_ts = node.get('_latest', (-1, ''))[0]
            if timestamp >= current_latest_ts:
                node['_latest'] = (timestamp, word)
        node['_end'] = True

    def query_time_range_lex_sort(self, start_ts, end_ts):
        """
        Finds all words in a time range, returning them sorted alphabetically.

        Args:
            start_ts (int): The start of the time window (inclusive).
            end_ts (int): The end of the time window (inclusive).

        Returns:
            list[str]: A lexicographically sorted list of words found in the
                       specified time range.

        Example:
            cli.add_word("apple", 10)
            cli.add_word("banana", 20)
            cli.query_time_range_lex_sort(5, 25)
            # Returns: ['apple', 'banana']
        """
        start_idx = bisect.bisect_left(self._time_sorted_list, (start_ts, ''))

        words_in_range = []
        for i in range(start_idx, len(self._time_sorted_list)):
            ts, word = self._time_sorted_list[i]
            if ts <= end_ts:
                words_in_range.append(word)
            else:
                break

        # --- THE FIX IS HERE ---
        # First, sort the list in-place.
        words_in_range.sort()
        # Then, return the list itself.
        return words_in_range

    def query_prefix_recent_timestamp(self, prefix):
        """
        Finds the timestamp of the most recent word starting with the given prefix.

        Args:
            prefix (str): The prefix to search for (e.g., "app").

        Returns:
            int | None: The timestamp of the most recent matching word. Returns
                        None if no words with that prefix exist in the index.

        Example:
            cli.add_word("apple", 10)
            cli.add_word("apply", 20)
            cli.query_prefix_recent_timestamp("app")
            # Returns: 20
        """
        node = self._prefix_trie
        for char in prefix:
            if char not in node:
                return None
            node = node[char]

        if '_latest' in node:
            return node['_latest'][0]
        else:
            return None


# =================
#  TESTS
# =================
def run_chrono_lex_index_tests():
    cli = ChronoLexIndex()
    cli.add_word("apple", 10)
    cli.add_word("apricot", 12)
    cli.add_word("banana", 15)
    cli.add_word("apply", 20)
    cli.add_word("bandana", 22)
    cli.add_word("cat", 30)

    # Test 1: Normal Case - Standard time range query
    result = cli.query_time_range_lex_sort(11, 25)
    expected = ['apply', 'apricot', 'banana', 'bandana']
    assert result == expected

    # Test 2: Normal Case - Standard prefix recency query
    assert cli.query_prefix_recent_timestamp("ap") == 20
    assert cli.query_prefix_recent_timestamp("ban") == 22

    # Test 3: Edge Case - Time range that contains no words
    assert cli.query_time_range_lex_sort(16, 19) == []

    # Test 4: Edge Case - Prefix that doesn't exist
    assert cli.query_prefix_recent_timestamp("dog") is None

    # Test 5: Long Case - Update changes a query's result
    cli.add_word("application", 25)
    assert cli.query_prefix_recent_timestamp("app") == 25

    # Test 6: Edge Case - Words with the exact same timestamp
    cli_tie = ChronoLexIndex()
    cli_tie.add_word("zeta", 10)
    cli_tie.add_word("alpha", 10)
    result = cli_tie.query_time_range_lex_sort(5, 15)
    assert result == ["alpha", "zeta"]

    # Test 7: Edge Case - Prefix is a full word, but a longer word is newer
    # "apple" (10) is a prefix of "applesauce" (26). Querying "apple" should find the newer one.
    cli.add_word("applesauce", 26)
    assert cli.query_prefix_recent_timestamp("apple") == 26

    # Test 8: Edge Case - Empty string prefix
    # A query for an empty prefix should return the timestamp of the most recently added word overall.
    assert cli.query_prefix_recent_timestamp("") == 30
    cli.add_word("zebra", 40)
    assert cli.query_prefix_recent_timestamp("") == 40

    print("✅ All 8 ChronoLexIndex tests passed!")


if __name__ == "__main__":
    run_chrono_lex_index_tests()