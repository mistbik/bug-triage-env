"""
Bug scenario data for the Bug Triage & Patch Validation environment.

Each scenario contains:
- buggy_code: The code with a bug
- correct_code: The fixed version
- test_code: Tests that pass on correct_code and fail on buggy_code
- bug_line: The line number of the bug (1-indexed)
- bug_description: A short description of the bug
- difficulty: easy | medium | hard
"""

SCENARIOS = [
    # ========== EASY SCENARIOS ==========
    {
        "id": "easy_off_by_one",
        "difficulty": "easy",
        "file_name": "utils.py",
        "task_description": (
            "A function that computes the sum of a list has a bug. "
            "Find the bug, identify the root cause, and submit a fix."
        ),
        "buggy_code": (
            "def sum_list(numbers):\n"
            "    \"\"\"Return the sum of all numbers in the list.\"\"\"\n"
            "    total = 0\n"
            "    for i in range(1, len(numbers)):\n"
            "        total += numbers[i]\n"
            "    return total\n"
        ),
        "correct_code": (
            "def sum_list(numbers):\n"
            "    \"\"\"Return the sum of all numbers in the list.\"\"\"\n"
            "    total = 0\n"
            "    for i in range(0, len(numbers)):\n"
            "        total += numbers[i]\n"
            "    return total\n"
        ),
        "test_code": (
            "def test_sum_list_basic():\n"
            "    assert sum_list([1, 2, 3]) == 6\n"
            "\n"
            "def test_sum_list_single():\n"
            "    assert sum_list([5]) == 5\n"
            "\n"
            "def test_sum_list_empty():\n"
            "    assert sum_list([]) == 0\n"
            "\n"
            "def test_sum_list_negative():\n"
            "    assert sum_list([-1, -2, -3]) == -6\n"
        ),
        "bug_line": 4,
        "bug_description": "Off-by-one error: range starts at 1 instead of 0, skipping the first element.",
    },
    {
        "id": "easy_wrong_operator",
        "difficulty": "easy",
        "file_name": "math_utils.py",
        "task_description": (
            "A function that calculates the average of a list returns wrong results. "
            "Find the bug and fix it."
        ),
        "buggy_code": (
            "def average(numbers):\n"
            "    \"\"\"Return the arithmetic mean of a list of numbers.\"\"\"\n"
            "    if not numbers:\n"
            "        return 0.0\n"
            "    return sum(numbers) // len(numbers)\n"
        ),
        "correct_code": (
            "def average(numbers):\n"
            "    \"\"\"Return the arithmetic mean of a list of numbers.\"\"\"\n"
            "    if not numbers:\n"
            "        return 0.0\n"
            "    return sum(numbers) / len(numbers)\n"
        ),
        "test_code": (
            "def test_average_basic():\n"
            "    assert average([2, 4, 6]) == 4.0\n"
            "\n"
            "def test_average_float():\n"
            "    assert abs(average([1, 2]) - 1.5) < 1e-9\n"
            "\n"
            "def test_average_empty():\n"
            "    assert average([]) == 0.0\n"
            "\n"
            "def test_average_single():\n"
            "    assert average([7]) == 7.0\n"
        ),
        "bug_line": 5,
        "bug_description": "Integer division (//) used instead of true division (/), truncating the result.",
    },
    {
        "id": "easy_wrong_return",
        "difficulty": "easy",
        "file_name": "string_utils.py",
        "task_description": (
            "A function that checks if a string is a palindrome is broken. "
            "Find the bug and fix it."
        ),
        "buggy_code": (
            "def is_palindrome(s):\n"
            "    \"\"\"Check if string s is a palindrome (case-insensitive).\"\"\"\n"
            "    cleaned = s.lower().replace(' ', '')\n"
            "    return cleaned != cleaned[::-1]\n"
        ),
        "correct_code": (
            "def is_palindrome(s):\n"
            "    \"\"\"Check if string s is a palindrome (case-insensitive).\"\"\"\n"
            "    cleaned = s.lower().replace(' ', '')\n"
            "    return cleaned == cleaned[::-1]\n"
        ),
        "test_code": (
            "def test_palindrome_true():\n"
            "    assert is_palindrome('racecar') is True\n"
            "\n"
            "def test_palindrome_false():\n"
            "    assert is_palindrome('hello') is False\n"
            "\n"
            "def test_palindrome_case():\n"
            "    assert is_palindrome('Racecar') is True\n"
            "\n"
            "def test_palindrome_spaces():\n"
            "    assert is_palindrome('nurses run') is True\n"
        ),
        "bug_line": 4,
        "bug_description": "Comparison uses != instead of ==, inverting the logic.",
    },
    # ========== MEDIUM SCENARIOS ==========
    {
        "id": "medium_boundary_check",
        "difficulty": "medium",
        "file_name": "search.py",
        "task_description": (
            "A binary search function sometimes returns wrong indices or crashes. "
            "Find and fix the bug. The function should return the index of the target "
            "or -1 if not found."
        ),
        "buggy_code": (
            "def binary_search(arr, target):\n"
            "    \"\"\"Return index of target in sorted arr, or -1 if not found.\"\"\"\n"
            "    low, high = 0, len(arr)\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1\n"
        ),
        "correct_code": (
            "def binary_search(arr, target):\n"
            "    \"\"\"Return index of target in sorted arr, or -1 if not found.\"\"\"\n"
            "    low, high = 0, len(arr) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1\n"
        ),
        "test_code": (
            "def test_binary_search_found():\n"
            "    assert binary_search([1, 3, 5, 7, 9], 5) == 2\n"
            "\n"
            "def test_binary_search_first():\n"
            "    assert binary_search([1, 3, 5, 7, 9], 1) == 0\n"
            "\n"
            "def test_binary_search_last():\n"
            "    assert binary_search([1, 3, 5, 7, 9], 9) == 4\n"
            "\n"
            "def test_binary_search_not_found():\n"
            "    assert binary_search([1, 3, 5, 7, 9], 4) == -1\n"
            "\n"
            "def test_binary_search_empty():\n"
            "    assert binary_search([], 1) == -1\n"
        ),
        "bug_line": 3,
        "bug_description": "high initialized to len(arr) instead of len(arr)-1, causing potential IndexError.",
    },
    {
        "id": "medium_logic_error",
        "difficulty": "medium",
        "file_name": "rate_limiter.py",
        "task_description": (
            "A rate limiter class that allows N requests per window has a bug. "
            "It should block requests when the limit is exceeded. "
            "Find and fix the bug."
        ),
        "buggy_code": (
            "class RateLimiter:\n"
            "    \"\"\"Simple sliding-window rate limiter.\"\"\"\n"
            "\n"
            "    def __init__(self, max_requests, window_seconds):\n"
            "        self.max_requests = max_requests\n"
            "        self.window_seconds = window_seconds\n"
            "        self.requests = []\n"
            "\n"
            "    def allow(self, timestamp):\n"
            "        \"\"\"Return True if request at given timestamp is allowed.\"\"\"\n"
            "        cutoff = timestamp - self.window_seconds\n"
            "        self.requests = [t for t in self.requests if t > cutoff]\n"
            "        if len(self.requests) < self.max_requests:\n"
            "            return True\n"
            "        return False\n"
        ),
        "correct_code": (
            "class RateLimiter:\n"
            "    \"\"\"Simple sliding-window rate limiter.\"\"\"\n"
            "\n"
            "    def __init__(self, max_requests, window_seconds):\n"
            "        self.max_requests = max_requests\n"
            "        self.window_seconds = window_seconds\n"
            "        self.requests = []\n"
            "\n"
            "    def allow(self, timestamp):\n"
            "        \"\"\"Return True if request at given timestamp is allowed.\"\"\"\n"
            "        cutoff = timestamp - self.window_seconds\n"
            "        self.requests = [t for t in self.requests if t > cutoff]\n"
            "        if len(self.requests) < self.max_requests:\n"
            "            self.requests.append(timestamp)\n"
            "            return True\n"
            "        return False\n"
        ),
        "test_code": (
            "def test_rate_limiter_allows_under_limit():\n"
            "    rl = RateLimiter(3, 10)\n"
            "    assert rl.allow(1) is True\n"
            "    assert rl.allow(2) is True\n"
            "    assert rl.allow(3) is True\n"
            "\n"
            "def test_rate_limiter_blocks_over_limit():\n"
            "    rl = RateLimiter(2, 10)\n"
            "    assert rl.allow(1) is True\n"
            "    assert rl.allow(2) is True\n"
            "    assert rl.allow(3) is False\n"
            "\n"
            "def test_rate_limiter_window_expires():\n"
            "    rl = RateLimiter(2, 5)\n"
            "    assert rl.allow(1) is True\n"
            "    assert rl.allow(2) is True\n"
            "    assert rl.allow(3) is False\n"
            "    assert rl.allow(8) is True\n"
            "\n"
            "def test_rate_limiter_single_request():\n"
            "    rl = RateLimiter(1, 10)\n"
            "    assert rl.allow(0) is True\n"
            "    assert rl.allow(1) is False\n"
        ),
        "bug_line": 13,
        "bug_description": "Allowed requests are never appended to self.requests, so the limiter never actually tracks usages and always allows.",
    },
    {
        "id": "medium_missing_edge",
        "difficulty": "medium",
        "file_name": "flatten.py",
        "task_description": (
            "A function to flatten a nested list is not handling all cases correctly. "
            "Find the bug and fix it."
        ),
        "buggy_code": (
            "def flatten(lst):\n"
            "    \"\"\"Flatten a nested list into a single list.\"\"\"\n"
            "    result = []\n"
            "    for item in lst:\n"
            "        if isinstance(item, list):\n"
            "            result.extend(item)\n"
            "        else:\n"
            "            result.append(item)\n"
            "    return result\n"
        ),
        "correct_code": (
            "def flatten(lst):\n"
            "    \"\"\"Flatten a nested list into a single list.\"\"\"\n"
            "    result = []\n"
            "    for item in lst:\n"
            "        if isinstance(item, list):\n"
            "            result.extend(flatten(item))\n"
            "        else:\n"
            "            result.append(item)\n"
            "    return result\n"
        ),
        "test_code": (
            "def test_flatten_basic():\n"
            "    assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]\n"
            "\n"
            "def test_flatten_deep():\n"
            "    assert flatten([1, [2, [3, [4]]]]) == [1, 2, 3, 4]\n"
            "\n"
            "def test_flatten_empty():\n"
            "    assert flatten([]) == []\n"
            "\n"
            "def test_flatten_no_nesting():\n"
            "    assert flatten([1, 2, 3]) == [1, 2, 3]\n"
            "\n"
            "def test_flatten_all_nested():\n"
            "    assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]\n"
        ),
        "bug_line": 6,
        "bug_description": "Uses extend(item) instead of extend(flatten(item)), failing to recursively flatten deeply nested lists.",
    },
    # ========== HARD SCENARIOS ==========
    {
        "id": "hard_concurrency_bug",
        "difficulty": "hard",
        "file_name": "lru_cache.py",
        "task_description": (
            "An LRU cache implementation has a subtle bug. The cache should evict "
            "the least recently used item when it exceeds capacity. Items that are "
            "accessed via get() should be marked as recently used. Find and fix the bug."
        ),
        "buggy_code": (
            "class LRUCache:\n"
            "    \"\"\"Least Recently Used cache with fixed capacity.\"\"\"\n"
            "\n"
            "    def __init__(self, capacity):\n"
            "        self.capacity = capacity\n"
            "        self.cache = {}  # key -> value\n"
            "        self.order = []  # access order, most recent at end\n"
            "\n"
            "    def get(self, key):\n"
            "        \"\"\"Get value by key. Returns -1 if not found.\"\"\"\n"
            "        if key not in self.cache:\n"
            "            return -1\n"
            "        return self.cache[key]\n"
            "\n"
            "    def put(self, key, value):\n"
            "        \"\"\"Insert or update key-value pair.\"\"\"\n"
            "        if key in self.cache:\n"
            "            self.order.remove(key)\n"
            "        elif len(self.cache) >= self.capacity:\n"
            "            oldest = self.order.pop(0)\n"
            "            del self.cache[oldest]\n"
            "        self.cache[key] = value\n"
            "        self.order.append(key)\n"
        ),
        "correct_code": (
            "class LRUCache:\n"
            "    \"\"\"Least Recently Used cache with fixed capacity.\"\"\"\n"
            "\n"
            "    def __init__(self, capacity):\n"
            "        self.capacity = capacity\n"
            "        self.cache = {}  # key -> value\n"
            "        self.order = []  # access order, most recent at end\n"
            "\n"
            "    def get(self, key):\n"
            "        \"\"\"Get value by key. Returns -1 if not found.\"\"\"\n"
            "        if key not in self.cache:\n"
            "            return -1\n"
            "        self.order.remove(key)\n"
            "        self.order.append(key)\n"
            "        return self.cache[key]\n"
            "\n"
            "    def put(self, key, value):\n"
            "        \"\"\"Insert or update key-value pair.\"\"\"\n"
            "        if key in self.cache:\n"
            "            self.order.remove(key)\n"
            "        elif len(self.cache) >= self.capacity:\n"
            "            oldest = self.order.pop(0)\n"
            "            del self.cache[oldest]\n"
            "        self.cache[key] = value\n"
            "        self.order.append(key)\n"
        ),
        "test_code": (
            "def test_lru_basic():\n"
            "    cache = LRUCache(2)\n"
            "    cache.put(1, 1)\n"
            "    cache.put(2, 2)\n"
            "    assert cache.get(1) == 1\n"
            "\n"
            "def test_lru_eviction():\n"
            "    cache = LRUCache(2)\n"
            "    cache.put(1, 1)\n"
            "    cache.put(2, 2)\n"
            "    cache.put(3, 3)  # evicts key 1\n"
            "    assert cache.get(1) == -1\n"
            "    assert cache.get(3) == 3\n"
            "\n"
            "def test_lru_access_refreshes():\n"
            "    cache = LRUCache(2)\n"
            "    cache.put(1, 1)\n"
            "    cache.put(2, 2)\n"
            "    cache.get(1)      # refresh key 1\n"
            "    cache.put(3, 3)   # should evict key 2, not key 1\n"
            "    assert cache.get(2) == -1\n"
            "    assert cache.get(1) == 1\n"
            "\n"
            "def test_lru_update_existing():\n"
            "    cache = LRUCache(2)\n"
            "    cache.put(1, 1)\n"
            "    cache.put(2, 2)\n"
            "    cache.put(1, 10)  # update key 1\n"
            "    assert cache.get(1) == 10\n"
            "\n"
            "def test_lru_not_found():\n"
            "    cache = LRUCache(2)\n"
            "    assert cache.get(99) == -1\n"
        ),
        "bug_line": 13,
        "bug_description": "get() does not update access order — it returns the value without moving the key to the end of the order list, so LRU eviction doesn't account for reads.",
    },
    {
        "id": "hard_state_machine",
        "difficulty": "hard",
        "file_name": "tokenizer.py",
        "task_description": (
            "A simple CSV tokenizer splits lines into fields, handling quoted fields "
            "that may contain commas. It has a bug that causes incorrect parsing of "
            "quoted fields. Find and fix the bug."
        ),
        "buggy_code": (
            "def parse_csv_line(line):\n"
            "    \"\"\"Parse a single CSV line into a list of fields.\n"
            "    Handles quoted fields that may contain commas.\"\"\"\n"
            "    fields = []\n"
            "    current = []\n"
            "    in_quotes = False\n"
            "    for char in line:\n"
            "        if char == '\"':\n"
            "            in_quotes = not in_quotes\n"
            "        elif char == ',' and not in_quotes:\n"
            "            fields.append(''.join(current))\n"
            "            current = []\n"
            "        else:\n"
            "            current.append(char)\n"
            "    if current:\n"
            "        fields.append(''.join(current))\n"
            "    return fields\n"
        ),
        "correct_code": (
            "def parse_csv_line(line):\n"
            "    \"\"\"Parse a single CSV line into a list of fields.\n"
            "    Handles quoted fields that may contain commas.\"\"\"\n"
            "    fields = []\n"
            "    current = []\n"
            "    in_quotes = False\n"
            "    for char in line:\n"
            "        if char == '\"':\n"
            "            in_quotes = not in_quotes\n"
            "        elif char == ',' and not in_quotes:\n"
            "            fields.append(''.join(current))\n"
            "            current = []\n"
            "        else:\n"
            "            current.append(char)\n"
            "    fields.append(''.join(current))\n"
            "    return fields\n"
        ),
        "test_code": (
            "def test_simple():\n"
            "    assert parse_csv_line('a,b,c') == ['a', 'b', 'c']\n"
            "\n"
            "def test_quoted():\n"
            "    assert parse_csv_line('\"hello, world\",b') == ['hello, world', 'b']\n"
            "\n"
            "def test_empty_fields():\n"
            "    assert parse_csv_line('a,,c') == ['a', '', 'c']\n"
            "\n"
            "def test_trailing_field():\n"
            "    assert parse_csv_line('a,b,') == ['a', 'b', '']\n"
            "\n"
            "def test_single_field():\n"
            "    assert parse_csv_line('hello') == ['hello']\n"
        ),
        "bug_line": 15,
        "bug_description": "The final field is only appended if 'current' is non-empty (truthy). An empty trailing field after the last comma is silently dropped.",
    },
    {
        "id": "hard_algorithm_bug",
        "difficulty": "hard",
        "file_name": "graph.py",
        "task_description": (
            "A function to detect cycles in a directed graph using DFS has a bug. "
            "It should return True if the graph contains a cycle. "
            "The graph is represented as an adjacency list (dict). "
            "Find and fix the bug."
        ),
        "buggy_code": (
            "def has_cycle(graph):\n"
            "    \"\"\"Detect if a directed graph has a cycle.\n"
            "    graph: dict mapping node -> list of neighbor nodes.\"\"\"\n"
            "    visited = set()\n"
            "\n"
            "    def dfs(node):\n"
            "        if node in visited:\n"
            "            return True\n"
            "        visited.add(node)\n"
            "        for neighbor in graph.get(node, []):\n"
            "            if dfs(neighbor):\n"
            "                return True\n"
            "        return False\n"
            "\n"
            "    for node in graph:\n"
            "        if dfs(node):\n"
            "            return True\n"
            "    return False\n"
        ),
        "correct_code": (
            "def has_cycle(graph):\n"
            "    \"\"\"Detect if a directed graph has a cycle.\n"
            "    graph: dict mapping node -> list of neighbor nodes.\"\"\"\n"
            "    visited = set()\n"
            "    rec_stack = set()\n"
            "\n"
            "    def dfs(node):\n"
            "        if node in rec_stack:\n"
            "            return True\n"
            "        if node in visited:\n"
            "            return False\n"
            "        visited.add(node)\n"
            "        rec_stack.add(node)\n"
            "        for neighbor in graph.get(node, []):\n"
            "            if dfs(neighbor):\n"
            "                return True\n"
            "        rec_stack.remove(node)\n"
            "        return False\n"
            "\n"
            "    for node in graph:\n"
            "        if dfs(node):\n"
            "            return True\n"
            "    return False\n"
        ),
        "test_code": (
            "def test_no_cycle():\n"
            "    g = {'a': ['b'], 'b': ['c'], 'c': []}\n"
            "    assert has_cycle(g) is False\n"
            "\n"
            "def test_simple_cycle():\n"
            "    g = {'a': ['b'], 'b': ['c'], 'c': ['a']}\n"
            "    assert has_cycle(g) is True\n"
            "\n"
            "def test_self_loop():\n"
            "    g = {'a': ['a']}\n"
            "    assert has_cycle(g) is True\n"
            "\n"
            "def test_dag_false_positive():\n"
            "    # Diamond DAG: a->b, a->c, b->d, c->d — no cycle\n"
            "    g = {'a': ['b', 'c'], 'b': ['d'], 'c': ['d'], 'd': []}\n"
            "    assert has_cycle(g) is False\n"
            "\n"
            "def test_disconnected_with_cycle():\n"
            "    g = {'a': ['b'], 'b': [], 'c': ['d'], 'd': ['c']}\n"
            "    assert has_cycle(g) is True\n"
        ),
        "bug_line": 7,
        "bug_description": "Uses a single 'visited' set instead of separating 'visited' and 'recursion stack'. This causes false positives on DAGs where a node is reachable via multiple paths (diamond pattern).",
    },
]


def get_scenarios_by_difficulty(difficulty: str):
    """Return scenarios matching the given difficulty."""
    return [s for s in SCENARIOS if s["difficulty"] == difficulty]


def get_scenario_by_id(scenario_id: str):
    """Return a single scenario by ID."""
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    return None
