import unittest

def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5  # Passes
    assert add(-1, 1) == 0  # Passes
    assert add(0, 0) == 0   # Passes

if __name__ == "__main__":
    unittest.main()
