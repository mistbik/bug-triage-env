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
    {'id': 'easy_off_by_one',
     'difficulty': 'easy',
     'file_name': 'utils.py',
     'task_description': 'A function that computes the sum of a list has a bug. Find the bug, identify the root cause, and '
                         'submit a fix.',
     'buggy_code': 'def sum_list(numbers):\n'
                   '    """Return the sum of all numbers in the list."""\n'
                   '    total = 0\n'
                   '    for i in range(1, len(numbers)):\n'
                   '        total += numbers[i]\n'
                   '    return total\n',
     'correct_code': 'def sum_list(numbers):\n'
                     '    """Return the sum of all numbers in the list."""\n'
                     '    total = 0\n'
                     '    for i in range(0, len(numbers)):\n'
                     '        total += numbers[i]\n'
                     '    return total\n',
     'test_code': 'def test_sum_list_basic():\n'
                  '    assert sum_list([1, 2, 3]) == 6\n'
                  '\n'
                  'def test_sum_list_single():\n'
                  '    assert sum_list([5]) == 5\n'
                  '\n'
                  'def test_sum_list_empty():\n'
                  '    assert sum_list([]) == 0\n'
                  '\n'
                  'def test_sum_list_negative():\n'
                  '    assert sum_list([-1, -2, -3]) == -6\n',
     'bug_line': 4,
     'bug_description': 'Off-by-one error: range starts at 1 instead of 0, skipping the first element.'},
    {'id': 'easy_wrong_operator',
     'difficulty': 'easy',
     'file_name': 'math_utils.py',
     'task_description': 'A function that calculates the average of a list returns wrong results. Find the bug and fix it.',
     'buggy_code': 'def average(numbers):\n'
                   '    """Return the arithmetic mean of a list of numbers."""\n'
                   '    if not numbers:\n'
                   '        return 0.0\n'
                   '    return sum(numbers) // len(numbers)\n',
     'correct_code': 'def average(numbers):\n'
                     '    """Return the arithmetic mean of a list of numbers."""\n'
                     '    if not numbers:\n'
                     '        return 0.0\n'
                     '    return sum(numbers) / len(numbers)\n',
     'test_code': 'def test_average_basic():\n'
                  '    assert average([2, 4, 6]) == 4.0\n'
                  '\n'
                  'def test_average_float():\n'
                  '    assert abs(average([1, 2]) - 1.5) < 1e-9\n'
                  '\n'
                  'def test_average_empty():\n'
                  '    assert average([]) == 0.0\n'
                  '\n'
                  'def test_average_single():\n'
                  '    assert average([7]) == 7.0\n',
     'bug_line': 5,
     'bug_description': 'Integer division (//) used instead of true division (/), truncating the result.'},
    {'id': 'easy_wrong_return',
     'difficulty': 'easy',
     'file_name': 'string_utils.py',
     'task_description': 'A function that checks if a string is a palindrome is broken. Find the bug and fix it.',
     'buggy_code': 'def is_palindrome(s):\n'
                   '    """Check if string s is a palindrome (case-insensitive)."""\n'
                   "    cleaned = s.lower().replace(' ', '')\n"
                   '    return cleaned != cleaned[::-1]\n',
     'correct_code': 'def is_palindrome(s):\n'
                     '    """Check if string s is a palindrome (case-insensitive)."""\n'
                     "    cleaned = s.lower().replace(' ', '')\n"
                     '    return cleaned == cleaned[::-1]\n',
     'test_code': 'def test_palindrome_true():\n'
                  "    assert is_palindrome('racecar') is True\n"
                  '\n'
                  'def test_palindrome_false():\n'
                  "    assert is_palindrome('hello') is False\n"
                  '\n'
                  'def test_palindrome_case():\n'
                  "    assert is_palindrome('Racecar') is True\n"
                  '\n'
                  'def test_palindrome_spaces():\n'
                  "    assert is_palindrome('nurses run') is True\n",
     'bug_line': 4,
     'bug_description': 'Comparison uses != instead of ==, inverting the logic.'},
    {'id': 'easy_wrong_comparison',
     'difficulty': 'easy',
     'file_name': 'clamp.py',
     'task_description': 'A function that clamps a value to a range [min_val, max_val] returns wrong results for some '
                         'inputs. Find the bug and fix it.',
     'buggy_code': 'def clamp(value, min_val, max_val):\n'
                   '    """Return value clamped to the range [min_val, max_val]."""\n'
                   '    if value < min_val:\n'
                   '        return min_val\n'
                   '    if value < max_val:\n'
                   '        return max_val\n'
                   '    return value\n',
     'correct_code': 'def clamp(value, min_val, max_val):\n'
                     '    """Return value clamped to the range [min_val, max_val]."""\n'
                     '    if value < min_val:\n'
                     '        return min_val\n'
                     '    if value > max_val:\n'
                     '        return max_val\n'
                     '    return value\n',
     'test_code': 'def test_clamp_below():\n'
                  '    assert clamp(1, 5, 10) == 5\n'
                  '\n'
                  'def test_clamp_above():\n'
                  '    assert clamp(15, 5, 10) == 10\n'
                  '\n'
                  'def test_clamp_within():\n'
                  '    assert clamp(7, 5, 10) == 7\n'
                  '\n'
                  'def test_clamp_exact_min():\n'
                  '    assert clamp(5, 5, 10) == 5\n'
                  '\n'
                  'def test_clamp_exact_max():\n'
                  '    assert clamp(10, 5, 10) == 10\n',
     'bug_line': 5,
     'bug_description': 'Second condition uses < instead of >, so values within the valid range are incorrectly clamped to '
                        'max_val.'},
    {'id': 'easy_missing_return',
     'difficulty': 'easy',
     'file_name': 'list_utils.py',
     'task_description': 'A function that finds the maximum value in a list always returns None. Find the bug and fix it.',
     'buggy_code': 'def find_max(numbers):\n'
                   '    """Return the maximum value in a non-empty list."""\n'
                   '    max_val = numbers[0]\n'
                   '    for n in numbers[1:]:\n'
                   '        if n > max_val:\n'
                   '            max_val = n\n',
     'correct_code': 'def find_max(numbers):\n'
                     '    """Return the maximum value in a non-empty list."""\n'
                     '    max_val = numbers[0]\n'
                     '    for n in numbers[1:]:\n'
                     '        if n > max_val:\n'
                     '            max_val = n\n'
                     '    return max_val\n',
     'test_code': 'def test_find_max_basic():\n'
                  '    assert find_max([3, 1, 4, 1, 5]) == 5\n'
                  '\n'
                  'def test_find_max_single():\n'
                  '    assert find_max([7]) == 7\n'
                  '\n'
                  'def test_find_max_negatives():\n'
                  '    assert find_max([-3, -1, -4]) == -1\n'
                  '\n'
                  'def test_find_max_duplicates():\n'
                  '    assert find_max([2, 2, 2]) == 2\n',
     'bug_line': 6,
     'bug_description': 'Missing return statement — the function computes max_val correctly but never returns it, so it '
                        'always returns None.'},
    {'id': 'medium_boundary_check',
     'difficulty': 'medium',
     'file_name': 'search.py',
     'task_description': 'A binary search function sometimes returns wrong indices or crashes. Find and fix the bug. The '
                         'function should return the index of the target or -1 if not found.',
     'buggy_code': 'def binary_search(arr, target):\n'
                   '    """Return index of target in sorted arr, or -1 if not found."""\n'
                   '    low, high = 0, len(arr)\n'
                   '    while low <= high:\n'
                   '        mid = (low + high) // 2\n'
                   '        if arr[mid] == target:\n'
                   '            return mid\n'
                   '        elif arr[mid] < target:\n'
                   '            low = mid + 1\n'
                   '        else:\n'
                   '            high = mid - 1\n'
                   '    return -1\n',
     'correct_code': 'def binary_search(arr, target):\n'
                     '    """Return index of target in sorted arr, or -1 if not found."""\n'
                     '    low, high = 0, len(arr) - 1\n'
                     '    while low <= high:\n'
                     '        mid = (low + high) // 2\n'
                     '        if arr[mid] == target:\n'
                     '            return mid\n'
                     '        elif arr[mid] < target:\n'
                     '            low = mid + 1\n'
                     '        else:\n'
                     '            high = mid - 1\n'
                     '    return -1\n',
     'test_code': 'def test_binary_search_found():\n'
                  '    assert binary_search([1, 3, 5, 7, 9], 5) == 2\n'
                  '\n'
                  'def test_binary_search_first():\n'
                  '    assert binary_search([1, 3, 5, 7, 9], 1) == 0\n'
                  '\n'
                  'def test_binary_search_last():\n'
                  '    assert binary_search([1, 3, 5, 7, 9], 9) == 4\n'
                  '\n'
                  'def test_binary_search_not_found():\n'
                  '    assert binary_search([1, 3, 5, 7, 9], 4) == -1\n'
                  '\n'
                  'def test_binary_search_empty():\n'
                  '    assert binary_search([], 1) == -1\n',
     'bug_line': 3,
     'bug_description': 'high initialized to len(arr) instead of len(arr)-1, causing potential IndexError.'},
    {'id': 'medium_logic_error',
     'difficulty': 'medium',
     'file_name': 'rate_limiter.py',
     'task_description': 'A rate limiter class that allows N requests per window has a bug. It should block requests when '
                         'the limit is exceeded. Find and fix the bug.',
     'buggy_code': 'class RateLimiter:\n'
                   '    """Simple sliding-window rate limiter."""\n'
                   '\n'
                   '    def __init__(self, max_requests, window_seconds):\n'
                   '        self.max_requests = max_requests\n'
                   '        self.window_seconds = window_seconds\n'
                   '        self.requests = []\n'
                   '\n'
                   '    def allow(self, timestamp):\n'
                   '        """Return True if request at given timestamp is allowed."""\n'
                   '        cutoff = timestamp - self.window_seconds\n'
                   '        self.requests = [t for t in self.requests if t > cutoff]\n'
                   '        if len(self.requests) < self.max_requests:\n'
                   '            return True\n'
                   '        return False\n',
     'correct_code': 'class RateLimiter:\n'
                     '    """Simple sliding-window rate limiter."""\n'
                     '\n'
                     '    def __init__(self, max_requests, window_seconds):\n'
                     '        self.max_requests = max_requests\n'
                     '        self.window_seconds = window_seconds\n'
                     '        self.requests = []\n'
                     '\n'
                     '    def allow(self, timestamp):\n'
                     '        """Return True if request at given timestamp is allowed."""\n'
                     '        cutoff = timestamp - self.window_seconds\n'
                     '        self.requests = [t for t in self.requests if t > cutoff]\n'
                     '        if len(self.requests) < self.max_requests:\n'
                     '            self.requests.append(timestamp)\n'
                     '            return True\n'
                     '        return False\n',
     'test_code': 'def test_rate_limiter_allows_under_limit():\n'
                  '    rl = RateLimiter(3, 10)\n'
                  '    assert rl.allow(1) is True\n'
                  '    assert rl.allow(2) is True\n'
                  '    assert rl.allow(3) is True\n'
                  '\n'
                  'def test_rate_limiter_blocks_over_limit():\n'
                  '    rl = RateLimiter(2, 10)\n'
                  '    assert rl.allow(1) is True\n'
                  '    assert rl.allow(2) is True\n'
                  '    assert rl.allow(3) is False\n'
                  '\n'
                  'def test_rate_limiter_window_expires():\n'
                  '    rl = RateLimiter(2, 5)\n'
                  '    assert rl.allow(1) is True\n'
                  '    assert rl.allow(2) is True\n'
                  '    assert rl.allow(3) is False\n'
                  '    assert rl.allow(8) is True\n'
                  '\n'
                  'def test_rate_limiter_single_request():\n'
                  '    rl = RateLimiter(1, 10)\n'
                  '    assert rl.allow(0) is True\n'
                  '    assert rl.allow(1) is False\n',
     'bug_line': 13,
     'bug_description': 'Allowed requests are never appended to self.requests, so the limiter never actually tracks usages '
                        'and always allows.'},
    {'id': 'medium_missing_edge',
     'difficulty': 'medium',
     'file_name': 'flatten.py',
     'task_description': 'A function to flatten a nested list is not handling all cases correctly. Find the bug and fix '
                         'it.',
     'buggy_code': 'def flatten(lst):\n'
                   '    """Flatten a nested list into a single list."""\n'
                   '    result = []\n'
                   '    for item in lst:\n'
                   '        if isinstance(item, list):\n'
                   '            result.extend(item)\n'
                   '        else:\n'
                   '            result.append(item)\n'
                   '    return result\n',
     'correct_code': 'def flatten(lst):\n'
                     '    """Flatten a nested list into a single list."""\n'
                     '    result = []\n'
                     '    for item in lst:\n'
                     '        if isinstance(item, list):\n'
                     '            result.extend(flatten(item))\n'
                     '        else:\n'
                     '            result.append(item)\n'
                     '    return result\n',
     'test_code': 'def test_flatten_basic():\n'
                  '    assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]\n'
                  '\n'
                  'def test_flatten_deep():\n'
                  '    assert flatten([1, [2, [3, [4]]]]) == [1, 2, 3, 4]\n'
                  '\n'
                  'def test_flatten_empty():\n'
                  '    assert flatten([]) == []\n'
                  '\n'
                  'def test_flatten_no_nesting():\n'
                  '    assert flatten([1, 2, 3]) == [1, 2, 3]\n'
                  '\n'
                  'def test_flatten_all_nested():\n'
                  '    assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]\n',
     'bug_line': 6,
     'bug_description': 'Uses extend(item) instead of extend(flatten(item)), failing to recursively flatten deeply nested '
                        'lists.'},
    {'id': 'medium_wrong_default',
     'difficulty': 'medium',
     'file_name': 'word_counter.py',
     'task_description': 'A word frequency counter always reports counts that are one too high. Find the bug and fix it.',
     'buggy_code': 'def group_by(items, key_fn):\n'
                   '    """Group items into a dict by key_fn(item)."""\n'
                   '    groups = {}\n'
                   '    for item in items:\n'
                   '        k = key_fn(item)\n'
                   '        if k not in groups:\n'
                   '            groups[k] = []\n'
                   '        groups[k].append(item)\n'
                   '    return groups\n'
                   '\n'
                   'def count_words(text):\n'
                   '    """Return word frequency dict from a string."""\n'
                   '    counts = {}\n'
                   '    for word in text.lower().split():\n'
                   '        counts[word] = counts.get(word, 1) + 1\n'
                   '    return counts\n',
     'correct_code': 'def group_by(items, key_fn):\n'
                     '    """Group items into a dict by key_fn(item)."""\n'
                     '    groups = {}\n'
                     '    for item in items:\n'
                     '        k = key_fn(item)\n'
                     '        if k not in groups:\n'
                     '            groups[k] = []\n'
                     '        groups[k].append(item)\n'
                     '    return groups\n'
                     '\n'
                     'def count_words(text):\n'
                     '    """Return word frequency dict from a string."""\n'
                     '    counts = {}\n'
                     '    for word in text.lower().split():\n'
                     '        counts[word] = counts.get(word, 0) + 1\n'
                     '    return counts\n',
     'test_code': 'def test_count_single():\n'
                  "    assert count_words('hello') == {'hello': 1}\n"
                  '\n'
                  'def test_count_repeated():\n'
                  "    assert count_words('hi hi hi') == {'hi': 3}\n"
                  '\n'
                  'def test_count_mixed():\n'
                  "    assert count_words('a b a') == {'a': 2, 'b': 1}\n"
                  '\n'
                  'def test_count_case():\n'
                  "    assert count_words('Hi hi') == {'hi': 2}\n"
                  '\n'
                  'def test_group_by_len():\n'
                  "    assert group_by(['a', 'bb', 'cc', 'd'], len) == {1: ['a', 'd'], 2: ['bb', 'cc']}\n",
     'bug_line': 15,
     'bug_description': 'dict.get() default is 1 instead of 0, so the first occurrence of every word is counted as 2.'},
    {'id': 'medium_mutation_bug',
     'difficulty': 'medium',
     'file_name': 'running_totals.py',
     'task_description': 'A function that computes running totals of a list is silently mutating the input list as a side '
                         'effect. Find the bug and fix it.',
     'buggy_code': 'def running_totals(numbers):\n'
                   '    """Return a list where each element is the cumulative sum up to that index."""\n'
                   '    totals = numbers\n'
                   '    for i in range(1, len(totals)):\n'
                   '        totals[i] = totals[i - 1] + totals[i]\n'
                   '    return totals\n',
     'correct_code': 'def running_totals(numbers):\n'
                     '    """Return a list where each element is the cumulative sum up to that index."""\n'
                     '    totals = list(numbers)\n'
                     '    for i in range(1, len(totals)):\n'
                     '        totals[i] = totals[i - 1] + totals[i]\n'
                     '    return totals\n',
     'test_code': 'def test_running_basic():\n'
                  '    assert running_totals([1, 2, 3, 4]) == [1, 3, 6, 10]\n'
                  '\n'
                  'def test_running_single():\n'
                  '    assert running_totals([5]) == [5]\n'
                  '\n'
                  'def test_running_zeros():\n'
                  '    assert running_totals([0, 0, 0]) == [0, 0, 0]\n'
                  '\n'
                  'def test_no_mutation():\n'
                  '    inp = [1, 2, 3]\n'
                  '    running_totals(inp)\n'
                  '    assert inp == [1, 2, 3]\n'
                  '\n'
                  'def test_running_negatives():\n'
                  '    assert running_totals([-1, -2, -3]) == [-1, -3, -6]\n',
     'bug_line': 3,
     'bug_description': "totals = numbers assigns a reference instead of a copy, so the function mutates the caller's list "
                        'and produces wrong results on subsequent calls.'},
    {'id': 'hard_concurrency_bug',
     'difficulty': 'hard',
     'file_name': 'lru_cache.py',
     'task_description': 'An LRU cache implementation has a subtle bug. The cache should evict the least recently used '
                         'item when it exceeds capacity. Items that are accessed via get() should be marked as recently '
                         'used. Find and fix the bug.',
     'buggy_code': 'class LRUCache:\n'
                   '    """Least Recently Used cache with fixed capacity."""\n'
                   '\n'
                   '    def __init__(self, capacity):\n'
                   '        self.capacity = capacity\n'
                   '        self.cache = {}  # key -> value\n'
                   '        self.order = []  # access order, most recent at end\n'
                   '\n'
                   '    def get(self, key):\n'
                   '        """Get value by key. Returns -1 if not found."""\n'
                   '        if key not in self.cache:\n'
                   '            return -1\n'
                   '        return self.cache[key]\n'
                   '\n'
                   '    def put(self, key, value):\n'
                   '        """Insert or update key-value pair."""\n'
                   '        if key in self.cache:\n'
                   '            self.order.remove(key)\n'
                   '        elif len(self.cache) >= self.capacity:\n'
                   '            oldest = self.order.pop(0)\n'
                   '            del self.cache[oldest]\n'
                   '        self.cache[key] = value\n'
                   '        self.order.append(key)\n',
     'correct_code': 'class LRUCache:\n'
                     '    """Least Recently Used cache with fixed capacity."""\n'
                     '\n'
                     '    def __init__(self, capacity):\n'
                     '        self.capacity = capacity\n'
                     '        self.cache = {}  # key -> value\n'
                     '        self.order = []  # access order, most recent at end\n'
                     '\n'
                     '    def get(self, key):\n'
                     '        """Get value by key. Returns -1 if not found."""\n'
                     '        if key not in self.cache:\n'
                     '            return -1\n'
                     '        self.order.remove(key)\n'
                     '        self.order.append(key)\n'
                     '        return self.cache[key]\n'
                     '\n'
                     '    def put(self, key, value):\n'
                     '        """Insert or update key-value pair."""\n'
                     '        if key in self.cache:\n'
                     '            self.order.remove(key)\n'
                     '        elif len(self.cache) >= self.capacity:\n'
                     '            oldest = self.order.pop(0)\n'
                     '            del self.cache[oldest]\n'
                     '        self.cache[key] = value\n'
                     '        self.order.append(key)\n',
     'test_code': 'def test_lru_basic():\n'
                  '    cache = LRUCache(2)\n'
                  '    cache.put(1, 1)\n'
                  '    cache.put(2, 2)\n'
                  '    assert cache.get(1) == 1\n'
                  '\n'
                  'def test_lru_eviction():\n'
                  '    cache = LRUCache(2)\n'
                  '    cache.put(1, 1)\n'
                  '    cache.put(2, 2)\n'
                  '    cache.put(3, 3)  # evicts key 1\n'
                  '    assert cache.get(1) == -1\n'
                  '    assert cache.get(3) == 3\n'
                  '\n'
                  'def test_lru_access_refreshes():\n'
                  '    cache = LRUCache(2)\n'
                  '    cache.put(1, 1)\n'
                  '    cache.put(2, 2)\n'
                  '    cache.get(1)      # refresh key 1\n'
                  '    cache.put(3, 3)   # should evict key 2, not key 1\n'
                  '    assert cache.get(2) == -1\n'
                  '    assert cache.get(1) == 1\n'
                  '\n'
                  'def test_lru_update_existing():\n'
                  '    cache = LRUCache(2)\n'
                  '    cache.put(1, 1)\n'
                  '    cache.put(2, 2)\n'
                  '    cache.put(1, 10)  # update key 1\n'
                  '    assert cache.get(1) == 10\n'
                  '\n'
                  'def test_lru_not_found():\n'
                  '    cache = LRUCache(2)\n'
                  '    assert cache.get(99) == -1\n',
     'bug_line': 13,
     'bug_description': 'get() does not update access order — it returns the value without moving the key to the end of '
                        "the order list, so LRU eviction doesn't account for reads."},
    {'id': 'hard_state_machine',
     'difficulty': 'hard',
     'file_name': 'tokenizer.py',
     'task_description': 'A simple CSV tokenizer splits lines into fields, handling quoted fields that may contain commas. '
                         'It has a bug that causes incorrect parsing of quoted fields. Find and fix the bug.',
     'buggy_code': 'def parse_csv_line(line):\n'
                   '    """Parse a single CSV line into a list of fields.\n'
                   '    Handles quoted fields that may contain commas."""\n'
                   '    fields = []\n'
                   '    current = []\n'
                   '    in_quotes = False\n'
                   '    for char in line:\n'
                   '        if char == \'"\':\n'
                   '            in_quotes = not in_quotes\n'
                   "        elif char == ',' and not in_quotes:\n"
                   "            fields.append(''.join(current))\n"
                   '            current = []\n'
                   '        else:\n'
                   '            current.append(char)\n'
                   '    if current:\n'
                   "        fields.append(''.join(current))\n"
                   '    return fields\n',
     'correct_code': 'def parse_csv_line(line):\n'
                     '    """Parse a single CSV line into a list of fields.\n'
                     '    Handles quoted fields that may contain commas."""\n'
                     '    fields = []\n'
                     '    current = []\n'
                     '    in_quotes = False\n'
                     '    for char in line:\n'
                     '        if char == \'"\':\n'
                     '            in_quotes = not in_quotes\n'
                     "        elif char == ',' and not in_quotes:\n"
                     "            fields.append(''.join(current))\n"
                     '            current = []\n'
                     '        else:\n'
                     '            current.append(char)\n'
                     "    fields.append(''.join(current))\n"
                     '    return fields\n',
     'test_code': 'def test_simple():\n'
                  "    assert parse_csv_line('a,b,c') == ['a', 'b', 'c']\n"
                  '\n'
                  'def test_quoted():\n'
                  '    assert parse_csv_line(\'"hello, world",b\') == [\'hello, world\', \'b\']\n'
                  '\n'
                  'def test_empty_fields():\n'
                  "    assert parse_csv_line('a,,c') == ['a', '', 'c']\n"
                  '\n'
                  'def test_trailing_field():\n'
                  "    assert parse_csv_line('a,b,') == ['a', 'b', '']\n"
                  '\n'
                  'def test_single_field():\n'
                  "    assert parse_csv_line('hello') == ['hello']\n",
     'bug_line': 15,
     'bug_description': "The final field is only appended if 'current' is non-empty (truthy). An empty trailing field "
                        'after the last comma is silently dropped.'},
    {'id': 'hard_algorithm_bug',
     'difficulty': 'hard',
     'file_name': 'graph.py',
     'task_description': 'A function to detect cycles in a directed graph using DFS has a bug. It should return True if '
                         'the graph contains a cycle. The graph is represented as an adjacency list (dict). Find and fix '
                         'the bug.',
     'buggy_code': 'def has_cycle(graph):\n'
                   '    """Detect if a directed graph has a cycle.\n'
                   '    graph: dict mapping node -> list of neighbor nodes."""\n'
                   '    visited = set()\n'
                   '\n'
                   '    def dfs(node):\n'
                   '        if node in visited:\n'
                   '            return True\n'
                   '        visited.add(node)\n'
                   '        for neighbor in graph.get(node, []):\n'
                   '            if dfs(neighbor):\n'
                   '                return True\n'
                   '        return False\n'
                   '\n'
                   '    for node in graph:\n'
                   '        if dfs(node):\n'
                   '            return True\n'
                   '    return False\n',
     'correct_code': 'def has_cycle(graph):\n'
                     '    """Detect if a directed graph has a cycle.\n'
                     '    graph: dict mapping node -> list of neighbor nodes."""\n'
                     '    visited = set()\n'
                     '    rec_stack = set()\n'
                     '\n'
                     '    def dfs(node):\n'
                     '        if node in rec_stack:\n'
                     '            return True\n'
                     '        if node in visited:\n'
                     '            return False\n'
                     '        visited.add(node)\n'
                     '        rec_stack.add(node)\n'
                     '        for neighbor in graph.get(node, []):\n'
                     '            if dfs(neighbor):\n'
                     '                return True\n'
                     '        rec_stack.remove(node)\n'
                     '        return False\n'
                     '\n'
                     '    for node in graph:\n'
                     '        if dfs(node):\n'
                     '            return True\n'
                     '    return False\n',
     'test_code': 'def test_no_cycle():\n'
                  "    g = {'a': ['b'], 'b': ['c'], 'c': []}\n"
                  '    assert has_cycle(g) is False\n'
                  '\n'
                  'def test_simple_cycle():\n'
                  "    g = {'a': ['b'], 'b': ['c'], 'c': ['a']}\n"
                  '    assert has_cycle(g) is True\n'
                  '\n'
                  'def test_self_loop():\n'
                  "    g = {'a': ['a']}\n"
                  '    assert has_cycle(g) is True\n'
                  '\n'
                  'def test_dag_false_positive():\n'
                  '    # Diamond DAG: a->b, a->c, b->d, c->d — no cycle\n'
                  "    g = {'a': ['b', 'c'], 'b': ['d'], 'c': ['d'], 'd': []}\n"
                  '    assert has_cycle(g) is False\n'
                  '\n'
                  'def test_disconnected_with_cycle():\n'
                  "    g = {'a': ['b'], 'b': [], 'c': ['d'], 'd': ['c']}\n"
                  '    assert has_cycle(g) is True\n',
     'bug_line': 7,
     'bug_description': "Uses a single 'visited' set instead of separating 'visited' and 'recursion stack'. This causes "
                        'false positives on DAGs where a node is reachable via multiple paths (diamond pattern).'},
    {'id': 'hard_scope_bug',
     'difficulty': 'hard',
     'file_name': 'closures.py',
     'task_description': 'A factory function that creates a list of multiplier functions has a bug. All returned functions '
                         'behave identically instead of each using a different multiplier. Find and fix the bug.',
     'buggy_code': 'def make_multipliers(n):\n'
                   '    """Return a list of n functions where the i-th function multiplies its argument by i."""\n'
                   '    funcs = []\n'
                   '    for i in range(n):\n'
                   '        funcs.append(lambda x: i * x)\n'
                   '    return funcs\n',
     'correct_code': 'def make_multipliers(n):\n'
                     '    """Return a list of n functions where the i-th function multiplies its argument by i."""\n'
                     '    funcs = []\n'
                     '    for i in range(n):\n'
                     '        funcs.append(lambda x, i=i: i * x)\n'
                     '    return funcs\n',
     'test_code': 'def test_multipliers_values():\n'
                  '    fns = make_multipliers(4)\n'
                  '    assert fns[0](10) == 0\n'
                  '    assert fns[1](10) == 10\n'
                  '    assert fns[2](10) == 20\n'
                  '    assert fns[3](10) == 30\n'
                  '\n'
                  'def test_multipliers_count():\n'
                  '    assert len(make_multipliers(5)) == 5\n'
                  '\n'
                  'def test_multipliers_zero():\n'
                  '    fns = make_multipliers(3)\n'
                  '    assert fns[0](999) == 0\n'
                  '\n'
                  'def test_multipliers_independent():\n'
                  '    fns = make_multipliers(3)\n'
                  '    assert fns[1](5) == 5\n'
                  '    assert fns[2](5) == 10\n',
     'bug_line': 5,
     'bug_description': 'Lambda captures the loop variable i by reference, not by value. All closures share the same i, '
                        'which equals n-1 after the loop ends.'},
    {'id': 'hard_memoization_bug',
     'difficulty': 'hard',
     'file_name': 'memoize.py',
     'task_description': 'A memoization decorator has a subtle Python gotcha: it uses a mutable default argument for the '
                         'cache. This causes all memoized functions to share the same cache dict across calls. Find and '
                         'fix the bug.',
     'buggy_code': 'def memoize(fn, cache={}):\n'
                   '    """Return a memoized version of fn."""\n'
                   '    def wrapper(*args):\n'
                   '        if args not in cache:\n'
                   '            cache[args] = fn(*args)\n'
                   '        return cache[args]\n'
                   '    return wrapper\n',
     'correct_code': 'def memoize(fn, cache=None):\n'
                     '    """Return a memoized version of fn."""\n'
                     '    if cache is None:\n'
                     '        cache = {}\n'
                     '    def wrapper(*args):\n'
                     '        if args not in cache:\n'
                     '            cache[args] = fn(*args)\n'
                     '        return cache[args]\n'
                     '    return wrapper\n',
     'test_code': 'def test_memoize_correct():\n'
                  '    fn = memoize(lambda x: x * x)\n'
                  '    assert fn(4) == 16\n'
                  '\n'
                  'def test_memoize_caches():\n'
                  '    calls = []\n'
                  '    def track(x):\n'
                  '        calls.append(x)\n'
                  '        return x + 1\n'
                  '    f = memoize(track)\n'
                  '    f(5)\n'
                  '    f(5)\n'
                  '    assert len(calls) == 1\n'
                  '\n'
                  'def test_memoize_independent():\n'
                  '    f1 = memoize(lambda x: x + 1)\n'
                  '    f2 = memoize(lambda x: x + 2)\n'
                  '    assert f1(10) == 11\n'
                  '    assert f2(10) == 12\n'
                  '\n'
                  'def test_memoize_no_shared_cache():\n'
                  '    def fn_a(x): return x * 2\n'
                  '    def fn_b(x): return x * 3\n'
                  '    a = memoize(fn_a)\n'
                  '    b = memoize(fn_b)\n'
                  '    assert a(5) == 10\n'
                  '    assert b(5) == 15\n',
     'bug_line': 1,
     'bug_description': 'Mutable default argument cache={} is shared across all calls to memoize(). Every memoized '
                        'function writes into the same dict, causing cache collisions between unrelated functions.'},
    {'id': 'easy_wrong_init',
     'difficulty': 'easy',
     'file_name': 'vowels.py',
     'task_description': 'A function that counts vowels in a string always returns a count that is one too high. Find the '
                         'bug and fix it.',
     'buggy_code': 'def count_vowels(s):\n'
                   '    """Return the number of vowels in string s."""\n'
                   '    count = 1\n'
                   '    for ch in s.lower():\n'
                   "        if ch in 'aeiou':\n"
                   '            count += 1\n'
                   '    return count\n',
     'correct_code': 'def count_vowels(s):\n'
                     '    """Return the number of vowels in string s."""\n'
                     '    count = 0\n'
                     '    for ch in s.lower():\n'
                     "        if ch in 'aeiou':\n"
                     '            count += 1\n'
                     '    return count\n',
     'test_code': 'def test_basic():\n'
                  "    assert count_vowels('hello') == 2\n"
                  '\n'
                  'def test_empty():\n'
                  "    assert count_vowels('') == 0\n"
                  '\n'
                  'def test_no_vowels():\n'
                  "    assert count_vowels('gym') == 0\n"
                  '\n'
                  'def test_all_vowels():\n'
                  "    assert count_vowels('aeiou') == 5\n",
     'bug_line': 3,
     'bug_description': 'Counter initialised to 1 instead of 0, so every result is inflated by one.'},
    {'id': 'medium_index_error',
     'difficulty': 'medium',
     'file_name': 'rotate.py',
     'task_description': 'A function that rotates a list left by k positions produces incorrect results. Find the bug and '
                         'fix it.',
     'buggy_code': 'def rotate_list(lst, k):\n'
                   '    """Rotate list left by k positions."""\n'
                   '    if not lst:\n'
                   '        return lst\n'
                   '    k = k % len(lst)\n'
                   '    return lst[k:] + lst[:k - 1]\n',
     'correct_code': 'def rotate_list(lst, k):\n'
                     '    """Rotate list left by k positions."""\n'
                     '    if not lst:\n'
                     '        return lst\n'
                     '    k = k % len(lst)\n'
                     '    return lst[k:] + lst[:k]\n',
     'test_code': 'def test_rotate_basic():\n'
                  '    assert rotate_list([1,2,3,4,5], 2) == [3,4,5,1,2]\n'
                  '\n'
                  'def test_rotate_zero():\n'
                  '    assert rotate_list([1,2,3], 0) == [1,2,3]\n'
                  '\n'
                  'def test_rotate_full():\n'
                  '    assert rotate_list([1,2,3], 3) == [1,2,3]\n'
                  '\n'
                  'def test_rotate_one():\n'
                  '    assert rotate_list([1,2,3], 1) == [2,3,1]\n'
                  '\n'
                  'def test_rotate_empty():\n'
                  '    assert rotate_list([], 5) == []\n',
     'bug_line': 6,
     'bug_description': 'Slice lst[:k - 1] drops the last element of the prefix; should be lst[:k].'},
    {'id': 'medium_sentinel_bug',
     'difficulty': 'medium',
     'file_name': 'duplicates.py',
     'task_description': 'A function that finds the first duplicate in a list returns -1 instead of None when no duplicate '
                         'exists. Find the bug and fix it.',
     'buggy_code': 'def first_duplicate(lst):\n'
                   '    """Return the first element that appears more than once, or None."""\n'
                   '    seen = set()\n'
                   '    for item in lst:\n'
                   '        if item in seen:\n'
                   '            return item\n'
                   '        seen.add(item)\n'
                   '    return -1\n',
     'correct_code': 'def first_duplicate(lst):\n'
                     '    """Return the first element that appears more than once, or None."""\n'
                     '    seen = set()\n'
                     '    for item in lst:\n'
                     '        if item in seen:\n'
                     '            return item\n'
                     '        seen.add(item)\n'
                     '    return None\n',
     'test_code': 'def test_has_duplicate():\n'
                  '    assert first_duplicate([1,2,3,2,4]) == 2\n'
                  '\n'
                  'def test_no_duplicate():\n'
                  '    assert first_duplicate([1,2,3]) is None\n'
                  '\n'
                  'def test_empty():\n'
                  '    assert first_duplicate([]) is None\n'
                  '\n'
                  'def test_first_is_dup():\n'
                  '    assert first_duplicate([5,5,6]) == 5\n'
                  '\n'
                  'def test_negative_sentinel():\n'
                  '    assert first_duplicate([1,2,3]) != -1\n',
     'bug_line': 8,
     'bug_description': "Returns -1 as a sentinel instead of None, breaking callers that check 'is None'."},
    {'id': 'hard_accumulator_bug',
     'difficulty': 'hard',
     'file_name': 'anagrams.py',
     'task_description': 'A function that groups anagram words together has a bug. It crashes or returns wrong results '
                         'when a new anagram group is created. Find the bug and fix it.',
     'buggy_code': 'def group_anagrams(words):\n'
                   '    """Group words that are anagrams of each other."""\n'
                   '    groups = {}\n'
                   '    for word in words:\n'
                   "        key = ''.join(sorted(word))\n"
                   '        if key in groups:\n'
                   '            groups[key].append(word)\n'
                   '        else:\n'
                   '            groups[key] = word\n'
                   '    return list(groups.values())\n',
     'correct_code': 'def group_anagrams(words):\n'
                     '    """Group words that are anagrams of each other."""\n'
                     '    groups = {}\n'
                     '    for word in words:\n'
                     "        key = ''.join(sorted(word))\n"
                     '        if key in groups:\n'
                     '            groups[key].append(word)\n'
                     '        else:\n'
                     '            groups[key] = [word]\n'
                     '    return list(groups.values())\n',
     'test_code': 'def test_basic():\n'
                  "    result = group_anagrams(['eat','tea','tan','ate','nat','bat'])\n"
                  '    result_sets = [set(g) for g in result]\n'
                  "    assert {'eat','tea','ate'} in result_sets\n"
                  "    assert {'tan','nat'} in result_sets\n"
                  "    assert {'bat'} in result_sets\n"
                  '\n'
                  'def test_no_anagrams():\n'
                  "    result = group_anagrams(['abc','def'])\n"
                  '    assert len(result) == 2\n'
                  '\n'
                  'def test_all_anagrams():\n'
                  "    result = group_anagrams(['ab','ba'])\n"
                  '    assert len(result) == 1\n'
                  "    assert set(result[0]) == {'ab','ba'}\n"
                  '\n'
                  'def test_single():\n'
                  "    result = group_anagrams(['hello'])\n"
                  "    assert result == [['hello']]\n",
     'bug_line': 9,
     'bug_description': 'New group initialised as a bare string (groups[key] = word) instead of a list ([word]), so '
                        '.append() fails on first access.'},
    {'id': 'hard_recursion_bug',
     'difficulty': 'hard',
     'file_name': 'sort_utils.py',
     'task_description': 'A file contains a merge sort implementation and a median function that uses it. The sort is '
                         'correct but the median calculation is wrong for even-length lists. Find the bug and fix it.',
     'buggy_code': 'def merge_sort(lst):\n'
                   '    """Sort a list using merge sort. Returns a new sorted list."""\n'
                   '    if len(lst) <= 1:\n'
                   '        return lst\n'
                   '    mid = len(lst) // 2\n'
                   '    left = merge_sort(lst[:mid])\n'
                   '    right = merge_sort(lst[mid:])\n'
                   '    return merge(left, right)\n'
                   '\n'
                   'def merge(left, right):\n'
                   '    result = []\n'
                   '    i = j = 0\n'
                   '    while i < len(left) and j < len(right):\n'
                   '        if left[i] <= right[j]:\n'
                   '            result.append(left[i])\n'
                   '            i += 1\n'
                   '        else:\n'
                   '            result.append(right[j])\n'
                   '            j += 1\n'
                   '    result.extend(left[i:])\n'
                   '    result.extend(right[j:])\n'
                   '    return result\n'
                   '\n'
                   'def median(lst):\n'
                   '    """Return the median of a non-empty list."""\n'
                   '    sorted_lst = merge_sort(lst)\n'
                   '    n = len(sorted_lst)\n'
                   '    if n % 2 == 0:\n'
                   '        return (sorted_lst[n // 2] + sorted_lst[n // 2 + 1]) / 2\n'
                   '    return sorted_lst[n // 2]\n',
     'correct_code': 'def merge_sort(lst):\n'
                     '    """Sort a list using merge sort. Returns a new sorted list."""\n'
                     '    if len(lst) <= 1:\n'
                     '        return lst\n'
                     '    mid = len(lst) // 2\n'
                     '    left = merge_sort(lst[:mid])\n'
                     '    right = merge_sort(lst[mid:])\n'
                     '    return merge(left, right)\n'
                     '\n'
                     'def merge(left, right):\n'
                     '    result = []\n'
                     '    i = j = 0\n'
                     '    while i < len(left) and j < len(right):\n'
                     '        if left[i] <= right[j]:\n'
                     '            result.append(left[i])\n'
                     '            i += 1\n'
                     '        else:\n'
                     '            result.append(right[j])\n'
                     '            j += 1\n'
                     '    result.extend(left[i:])\n'
                     '    result.extend(right[j:])\n'
                     '    return result\n'
                     '\n'
                     'def median(lst):\n'
                     '    """Return the median of a non-empty list."""\n'
                     '    sorted_lst = merge_sort(lst)\n'
                     '    n = len(sorted_lst)\n'
                     '    if n % 2 == 0:\n'
                     '        return (sorted_lst[n // 2 - 1] + sorted_lst[n // 2]) / 2\n'
                     '    return sorted_lst[n // 2]\n',
     'test_code': 'def test_sort_basic():\n'
                  '    assert merge_sort([3,1,2]) == [1,2,3]\n'
                  '\n'
                  'def test_sort_empty():\n'
                  '    assert merge_sort([]) == []\n'
                  '\n'
                  'def test_sort_single():\n'
                  '    assert merge_sort([1]) == [1]\n'
                  '\n'
                  'def test_median_odd():\n'
                  '    assert median([3,1,2]) == 2\n'
                  '\n'
                  'def test_median_even():\n'
                  '    assert median([1,2,3,4]) == 2.5\n'
                  '\n'
                  'def test_median_even2():\n'
                  '    assert median([1,3,5,7]) == 4.0\n',
     'bug_line': 29,
     'bug_description': 'Even-length median averages indices n//2 and n//2+1 (both in the upper half) instead of n//2-1 '
                        'and n//2 (the two middle elements).'},
    {'id': 'multi_interface_mismatch',
     'difficulty': 'hard',
     'file_name': 'stack_calculator.py',
     'task_description': 'This file contains two components: a Stack class and an RPNCalculator that uses it. The '
                         'calculator works correctly but Stack.peek() crashes. The bug is an interface mismatch between '
                         'the two components — find which key name is inconsistent and fix it.',
     'buggy_code': '# --- stack.py ---\n'
                   'class Stack:\n'
                   '    def __init__(self):\n'
                   '        self._data = []\n'
                   '    def push(self, item):\n'
                   "        self._data.append({'val': item})\n"
                   '    def pop(self):\n'
                   "        return self._data.pop()['val']\n"
                   '    def peek(self):\n'
                   "        return self._data[-1]['value']\n"
                   '    def is_empty(self):\n'
                   '        return len(self._data) == 0\n'
                   '\n'
                   '# --- calculator.py ---\n'
                   'class RPNCalculator:\n'
                   '    """Evaluate Reverse Polish Notation expressions using Stack."""\n'
                   '    def __init__(self):\n'
                   '        self.stack = Stack()\n'
                   '    def evaluate(self, tokens):\n'
                   '        for token in tokens:\n'
                   '            if isinstance(token, (int, float)):\n'
                   '                self.stack.push(token)\n'
                   '            else:\n'
                   '                b = self.stack.pop()\n'
                   '                a = self.stack.pop()\n'
                   "                if token == '+': self.stack.push(a + b)\n"
                   "                elif token == '-': self.stack.push(a - b)\n"
                   "                elif token == '*': self.stack.push(a * b)\n"
                   "                elif token == '/': self.stack.push(a / b)\n"
                   '        return self.stack.pop()\n',
     'correct_code': '# --- stack.py ---\n'
                     'class Stack:\n'
                     '    def __init__(self):\n'
                     '        self._data = []\n'
                     '    def push(self, item):\n'
                     "        self._data.append({'val': item})\n"
                     '    def pop(self):\n'
                     "        return self._data.pop()['val']\n"
                     '    def peek(self):\n'
                     "        return self._data[-1]['val']\n"
                     '    def is_empty(self):\n'
                     '        return len(self._data) == 0\n'
                     '\n'
                     '# --- calculator.py ---\n'
                     'class RPNCalculator:\n'
                     '    """Evaluate Reverse Polish Notation expressions using Stack."""\n'
                     '    def __init__(self):\n'
                     '        self.stack = Stack()\n'
                     '    def evaluate(self, tokens):\n'
                     '        for token in tokens:\n'
                     '            if isinstance(token, (int, float)):\n'
                     '                self.stack.push(token)\n'
                     '            else:\n'
                     '                b = self.stack.pop()\n'
                     '                a = self.stack.pop()\n'
                     "                if token == '+': self.stack.push(a + b)\n"
                     "                elif token == '-': self.stack.push(a - b)\n"
                     "                elif token == '*': self.stack.push(a * b)\n"
                     "                elif token == '/': self.stack.push(a / b)\n"
                     '        return self.stack.pop()\n',
     'test_code': 'def test_stack_peek():\n'
                  '    s = Stack()\n'
                  '    s.push(42)\n'
                  '    assert s.peek() == 42\n'
                  '\n'
                  'def test_stack_pop():\n'
                  '    s = Stack()\n'
                  '    s.push(7)\n'
                  '    assert s.pop() == 7\n'
                  '\n'
                  'def test_rpn_add():\n'
                  '    calc = RPNCalculator()\n'
                  "    assert calc.evaluate([3, 4, '+']) == 7\n"
                  '\n'
                  'def test_rpn_complex():\n'
                  '    calc = RPNCalculator()\n'
                  "    assert calc.evaluate([2, 3, '*', 4, '+']) == 10\n"
                  '\n'
                  'def test_stack_is_empty():\n'
                  '    s = Stack()\n'
                  '    assert s.is_empty()\n'
                  '    s.push(1)\n'
                  '    assert not s.is_empty()\n',
     'bug_line': 10,
     'bug_description': "Stack.peek() reads key 'value' but push() stores key 'val' — interface mismatch between the two "
                        'methods causes a KeyError.'},
    {'id': 'multi_wrong_delegation',
     'difficulty': 'hard',
     'file_name': 'event_system.py',
     'task_description': 'This file contains an EventBus and a Notifier that subscribes to it. Events are published but '
                         'handlers are never called. The bug spans both components — find the cross-component '
                         'inconsistency and fix it.',
     'buggy_code': '# --- event_bus.py ---\n'
                   'class EventBus:\n'
                   '    """Simple synchronous event bus."""\n'
                   '    def __init__(self):\n'
                   '        self._handlers = {}\n'
                   '    def subscribe(self, event_type, handler):\n'
                   '        key = event_type.upper()\n'
                   '        if key not in self._handlers:\n'
                   '            self._handlers[key] = []\n'
                   '        self._handlers[key].append(handler)\n'
                   '    def publish(self, event_type, data=None):\n'
                   '        for handler in self._handlers.get(event_type, []):\n'
                   '            handler(data)\n'
                   '\n'
                   '# --- notifier.py ---\n'
                   'class Notifier:\n'
                   '    """Sends alerts via the EventBus."""\n'
                   '    def __init__(self, bus):\n'
                   '        self.bus = bus\n'
                   '        self.alerts = []\n'
                   "        self.bus.subscribe('alert', self._on_alert)\n"
                   '    def _on_alert(self, message):\n'
                   '        self.alerts.append(message)\n'
                   '    def send(self, message):\n'
                   "        self.bus.publish('alert', message)\n",
     'correct_code': '# --- event_bus.py ---\n'
                     'class EventBus:\n'
                     '    """Simple synchronous event bus."""\n'
                     '    def __init__(self):\n'
                     '        self._handlers = {}\n'
                     '    def subscribe(self, event_type, handler):\n'
                     '        key = event_type\n'
                     '        if key not in self._handlers:\n'
                     '            self._handlers[key] = []\n'
                     '        self._handlers[key].append(handler)\n'
                     '    def publish(self, event_type, data=None):\n'
                     '        for handler in self._handlers.get(event_type, []):\n'
                     '            handler(data)\n'
                     '\n'
                     '# --- notifier.py ---\n'
                     'class Notifier:\n'
                     '    """Sends alerts via the EventBus."""\n'
                     '    def __init__(self, bus):\n'
                     '        self.bus = bus\n'
                     '        self.alerts = []\n'
                     "        self.bus.subscribe('alert', self._on_alert)\n"
                     '    def _on_alert(self, message):\n'
                     '        self.alerts.append(message)\n'
                     '    def send(self, message):\n'
                     "        self.bus.publish('alert', message)\n",
     'test_code': 'def test_notifier_receives():\n'
                  '    bus = EventBus()\n'
                  '    n = Notifier(bus)\n'
                  "    n.send('hello')\n"
                  "    assert n.alerts == ['hello']\n"
                  '\n'
                  'def test_notifier_multiple():\n'
                  '    bus = EventBus()\n'
                  '    n = Notifier(bus)\n'
                  "    n.send('a')\n"
                  "    n.send('b')\n"
                  "    assert n.alerts == ['a', 'b']\n"
                  '\n'
                  'def test_bus_no_handlers():\n'
                  '    bus = EventBus()\n'
                  "    bus.publish('noevent', 'data')\n"
                  '\n'
                  'def test_bus_multiple_subscribers():\n'
                  '    bus = EventBus()\n'
                  '    received = []\n'
                  "    bus.subscribe('x', lambda d: received.append(d))\n"
                  "    bus.subscribe('x', lambda d: received.append(d))\n"
                  "    bus.publish('x', 1)\n"
                  '    assert received == [1, 1]\n'
                  '\n'
                  'def test_notifier_empty():\n'
                  '    bus = EventBus()\n'
                  '    n = Notifier(bus)\n'
                  '    assert n.alerts == []\n',
     'bug_line': 7,
     'bug_description': 'subscribe() normalises the key with .upper() but publish() looks up the original case — handlers '
                        "are stored under 'ALERT' but looked up under 'alert', so they are never called."},
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
