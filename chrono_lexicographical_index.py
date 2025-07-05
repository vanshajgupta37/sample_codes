from typing import List, Tuple, Optional
import bisect

class ChronoLexIndex:
    """
    Indexes words by timestamp and prefix for efficient querying.
    Supports time-range queries (lexicographically sorted) and
    most recent word by prefix queries.
    """

    def __init__(self):
        """Initializes internal data structures."""
        self._time_sorted_list: List[Tuple[int, str]] = []
        self._prefix_trie: dict = {}

    def add_word(self, word: str, timestamp: int) -> None:
        """
        Adds a word and its timestamp to both time-sorted list and prefix trie.
        """
        bisect.insort(self._time_sorted_list, (timestamp, word))

        node = self._prefix_trie
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

    def query_time_range_lex_sort(self, start_ts: int, end_ts: int) -> List[str]:
        """
        Finds words in a time range and returns them alphabetically sorted.

        Example:
            >>> cli = ChronoLexIndex()
            >>> cli.add_word("apple", 10)
            >>> cli.add_word("banana", 20)
            >>> cli.query_time_range_lex_sort(5, 25)
            ['apple', 'banana']
        """
        start_idx = bisect.bisect_left(self._time_sorted_list, (start_ts, ''))
        words_in_range: List[str] = []
        for i in range(start_idx, len(self._time_sorted_list)):
            ts, word = self._time_sorted_list[i]
            if ts <= end_ts:
                words_in_range.append(word)
            else:
                break
        words_in_range.sort()
        return words_in_range

    def query_prefix_recent_timestamp(self, prefix: str) -> Optional[int]:
        """
        Finds the timestamp of the most recent word starting with the prefix.

        Example:
            >>> cli = ChronoLexIndex()
            >>> cli.add_word("apple", 10)
            >>> cli.add_word("apply", 20)
            >>> cli.query_prefix_recent_timestamp("app")
            20
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

# ====================== TEST CASES ======================

def test_one():
    cli = ChronoLexIndex()
    cli.add_word("apple", 10)
    cli.add_word("apricot", 12)
    cli.add_word("banana", 15)
    cli.add_word("apply", 20)
    cli.add_word("bandana", 22)
    cli.add_word("cat", 30)
    result = cli.query_time_range_lex_sort(11, 25)
    expected = ['apply', 'apricot', 'banana', 'bandana']
    assert result == expected

def test_two():
    cli = ChronoLexIndex()
    cli.add_word("apple", 10)
    cli.add_word("apricot", 12)
    cli.add_word("banana", 15)
    cli.add_word("apply", 20)
    cli.add_word("bandana", 22)
    cli.add_word("cat", 30)
    assert cli.query_prefix_recent_timestamp("ap") == 20
    assert cli.query_prefix_recent_timestamp("ban") == 22

def test_three():
    cli = ChronoLexIndex()
    assert cli.query_time_range_lex_sort(16, 19) == []

def test_four():
    cli = ChronoLexIndex()
    assert cli.query_prefix_recent_timestamp("dog") is None

def test_five():
    cli = ChronoLexIndex()
    cli.add_word("apple", 10)
    cli.add_word("application", 25)
    assert cli.query_prefix_recent_timestamp("app") == 25

def test_six():
    cli_tie = ChronoLexIndex()
    cli_tie.add_word("zeta", 10)
    cli_tie.add_word("alpha", 10)
    result = cli_tie.query_time_range_lex_sort(5, 15)
    assert result == ["alpha", "zeta"]

def test_seven():
    cli = ChronoLexIndex()
    cli.add_word("apple", 10)
    cli.add_word("applesauce", 26)
    assert cli.query_prefix_recent_timestamp("apple") == 26

def test_eight():
    cli = ChronoLexIndex()
    cli.add_word("cat", 30)
    assert cli.query_prefix_recent_timestamp("") == 30
    cli.add_word("zebra", 40)
    assert cli.query_prefix_recent_timestamp("") == 40
