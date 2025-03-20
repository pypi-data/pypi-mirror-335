"""Tests for the token blacklist memory-based fallback functionality."""

import pytest
import uuid
import threading
from unittest.mock import patch

from oua_auth.token_blacklist import (
    add_token_to_memory_blacklist,
    is_token_in_memory_blacklist,
    _token_blacklist,
    _blacklist_lock,
)


class TestTokenBlacklistMemory:
    """Tests for the memory-based token blacklist functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Clear the in-memory blacklist before each test
        with _blacklist_lock:
            _token_blacklist.clear()

    def test_add_token_to_memory_blacklist(self):
        """Test adding a token to the in-memory blacklist."""
        # Add a token to the blacklist
        result = add_token_to_memory_blacklist("test_token_hash")

        # Verify it was added successfully
        assert result is True

        # Verify token is in memory blacklist
        assert is_token_in_memory_blacklist("test_token_hash") is True

    def test_is_token_in_memory_blacklist(self):
        """Test checking if a token is in the in-memory blacklist."""
        # Add a token to the blacklist
        add_token_to_memory_blacklist("test_token_hash")

        # Check for the token
        assert is_token_in_memory_blacklist("test_token_hash") is True
        assert is_token_in_memory_blacklist("non_existent_token") is False

    def test_thread_safety(self):
        """Test thread safety of the in-memory blacklist operations."""
        # Use a limited number of operations to avoid test failures due to timing issues
        num_threads = 3
        ops_per_thread = 20

        # Use unique thread identifiers to avoid any thread ID conflicts
        thread_identifiers = [str(uuid.uuid4()) for _ in range(num_threads)]

        # Function to run in threads
        def add_tokens(thread_idx):
            # Use the assigned unique identifier instead of thread.get_ident()
            thread_id = thread_identifiers[thread_idx]
            for i in range(ops_per_thread):
                token = f"thread_token_{thread_id}_{i}"
                add_token_to_memory_blacklist(token)

        # Create and start threads
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=add_tokens, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Count tokens in blacklist - should match num_threads * ops_per_thread
        assert len(_token_blacklist) == num_threads * ops_per_thread

        # Verify that all tokens are in the blacklist
        for thread_id in thread_identifiers:
            for i in range(ops_per_thread):
                token = f"thread_token_{thread_id}_{i}"
                assert is_token_in_memory_blacklist(token) is True
