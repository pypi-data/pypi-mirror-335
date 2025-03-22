import pytest
import threading
import time
from at_common_workflow.core.context import Context

def test_context_operations():
    context = Context()
    
    # Test setting and getting values
    context.set("key1", "value1")
    assert context.get("key1") == "value1"
    
    # Test nested values
    context.set("nested", {"a": {"b": "value"}})
    assert context.get("nested.a.b") == "value"
    
    # Test missing keys
    with pytest.raises(KeyError):
        context.get("non_existent")
    
    assert context.get("non_existent", default="default") == "default"

def test_attribute_access():
    context = Context()
    
    # Test attribute setting and getting
    context.user_name = "John"
    assert context.user_name == "John"
    assert context.get("user_name") == "John"
    
    # Test attribute access with default
    assert context.get("non_existent_attr", "default") == "default"
    
    # Test attribute error
    with pytest.raises(KeyError):
        _ = context.non_existent_attr

def test_contains_operator():
    context = Context()
    context.set("a.b.c", "value")
    
    assert "a" in context
    assert "a.b" in context
    assert "a.b.c" in context
    assert "a.b.d" not in context
    assert "x" not in context

def test_repr_functionality():
    context = Context()
    context.name = "test"
    context.nested = {"key": "value"}
    
    repr_str = repr(context)
    assert repr_str.startswith("Context(")
    assert repr_str.endswith(")")
    assert "name" in repr_str
    assert "test" in repr_str
    assert "nested" in repr_str

def test_type_handling():
    context = Context()
    
    # Test various types
    test_values = {
        "int": 42,
        "float": 3.14,
        "bool": True,
        "list": [1, 2, 3],
        "dict": {"a": 1},
        "none": None,
        "complex": {"list": [{"nested": "value"}]}
    }
    
    for key, value in test_values.items():
        context.set(key, value)
        assert context.get(key) == value

def test_copy():
    # Test the copy method
    original = Context()
    original.set("simple", "value")
    original.set("nested", {"a": {"b": "nested_value"}})
    original.set("list", [1, 2, 3])
    
    # Create a copy
    copy = original.copy()
    
    # Verify copy has the same values
    assert copy.get("simple") == "value"
    assert copy.get("nested.a.b") == "nested_value"
    assert copy.get("list") == [1, 2, 3]
    
    # Verify modifying the copy doesn't affect the original
    copy.set("simple", "new_value")
    copy.set("nested.a.b", "new_nested_value")
    copy.set("list", [4, 5, 6])
    
    # Original should be unchanged
    assert original.get("simple") == "value"
    assert original.get("nested.a.b") == "nested_value"
    assert original.get("list") == [1, 2, 3]
    
    # Verify deep copy for nested structures
    copy.set("nested.a.c", "added_value")
    assert "nested.a.c" in copy
    assert "nested.a.c" not in original

def test_edge_cases():
    context = Context()
    
    # Test empty key
    with pytest.raises(KeyError):
        context.set("", "value")
    
    with pytest.raises(KeyError):
        context.get("")
    
    # Test None key
    with pytest.raises(AttributeError):
        context.set(None, "value")
    
    with pytest.raises(AttributeError):
        context.get(None)
    
    # Test overwriting non-dict with dict for nested keys
    context.set("key", "value")
    context.set("key.nested", "nested_value")
    assert context.get("key.nested") == "nested_value"
    # Original key is now a dict
    assert isinstance(context.get("key"), dict)

def test_thread_safety():
    context = Context()
    errors = []
    
    def worker(worker_id, iterations=1000):
        try:
            for i in range(iterations):
                key = f"worker{worker_id}_key{i}"
                value = f"value{i}"
                context.set(key, value)
                assert context.get(key) == value
        except Exception as e:
            errors.append(e)
    
    threads = []
    for i in range(5):  # Create 5 threads
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    assert not errors, f"Errors occurred during thread execution: {errors}"

def test_special_characters_in_keys():
    """Test that Context can handle special characters in keys."""
    context = Context()
    
    # Test with special characters
    special_keys = {
        "key-with-dashes": "dash-value",
        "key_with_underscores": "underscore_value",
        "key.with.dots": "dot.value",
        "key with spaces": "space value",
        "key@with@at": "at@value",
        "key#with#hash": "hash#value",
        "key&with&ampersand": "ampersand&value",
    }
    
    # Set all special character keys
    for key, value in special_keys.items():
        context.set(key, value)
    
    # Verify all keys can be retrieved
    for key, expected_value in special_keys.items():
        assert context.get(key) == expected_value
    
    # Test attribute access for keys that can be attributes
    context.key_with_underscores = "new_underscore_value"
    assert context.key_with_underscores == "new_underscore_value"
    
    # Test that keys with special characters that can't be attributes
    # can still be accessed via get()
    with pytest.raises(KeyError):
        _ = context.key_with_dashes
    
    assert context.get("key-with-dashes") == "dash-value"

def test_deep_nesting():
    """Test that Context can handle very deep nesting of keys."""
    context = Context()
    
    # Create a deeply nested structure
    depth = 50
    nested_key = ".".join([f"level{i}" for i in range(depth)])
    
    # Set the deeply nested value
    context.set(nested_key, "deep_value")
    
    # Verify we can retrieve the value
    assert context.get(nested_key) == "deep_value"
    
    # Verify intermediate levels are dictionaries
    for i in range(1, depth):
        partial_key = ".".join([f"level{j}" for j in range(i)])
        assert isinstance(context.get(partial_key), dict)
    
    # Test accessing a level too deep
    too_deep_key = nested_key + ".too_deep"
    with pytest.raises(KeyError):
        context.get(too_deep_key)

def test_large_data_volume():
    """Test that Context can handle large volumes of data."""
    context = Context()
    
    # Add a large number of keys
    num_keys = 1000
    for i in range(num_keys):
        context.set(f"key{i}", f"value{i}")
    
    # Verify all keys can be retrieved
    for i in range(num_keys):
        assert context.get(f"key{i}") == f"value{i}"
    
    # Add a key with a large value
    large_value = "x" * 1000000  # 1MB string
    context.set("large_value", large_value)
    assert context.get("large_value") == large_value
    
    # Test copying with large data
    copy = context.copy()
    assert copy.get("large_value") == large_value

def test_complex_concurrent_operations():
    """Test complex concurrent operations on Context."""
    context = Context()
    errors = []
    num_threads = 10
    operations_per_thread = 100
    
    # Initialize with some data
    context.set("shared_dict", {})
    context.set("shared_list", [])
    context.set("counter", 0)
    
    def worker(worker_id):
        try:
            # Perform a mix of operations
            for i in range(operations_per_thread):
                # Update counter
                current = context.get("counter")
                context.set("counter", current + 1)
                
                # Add to shared dict
                shared_dict = context.get("shared_dict")
                key = f"worker{worker_id}_item{i}"
                shared_dict[key] = i
                context.set("shared_dict", shared_dict)
                
                # Add to shared list
                shared_list = context.get("shared_list")
                shared_list.append(f"worker{worker_id}_item{i}")
                context.set("shared_list", shared_list)
                
                # Create nested path
                nested_key = f"workers.worker{worker_id}.items.{i}"
                context.set(nested_key, i)
                
                # Read some values to mix reads and writes
                assert context.get(nested_key) == i
                assert f"worker{worker_id}" in context.get("workers")
        except Exception as e:
            errors.append(f"Worker {worker_id} error: {str(e)}")
    
    # Start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify results
    assert not errors, f"Errors occurred: {errors}"
    
    # Check counter
    assert context.get("counter") == num_threads * operations_per_thread
    
    # Check shared dict
    shared_dict = context.get("shared_dict")
    assert len(shared_dict) == num_threads * operations_per_thread
    
    # Check shared list
    shared_list = context.get("shared_list")
    assert len(shared_list) == num_threads * operations_per_thread
    
    # Check nested paths
    for worker_id in range(num_threads):
        for i in range(operations_per_thread):
            assert context.get(f"workers.worker{worker_id}.items.{i}") == i