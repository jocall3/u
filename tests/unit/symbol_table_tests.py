import unittest
from typing import Any, Dict, Optional

class SymbolTable:
    """
    A symbol table for managing variables and their values in a hierarchical scope.
    """

    def __init__(self, parent: Optional['SymbolTable'] = None):
        """
        Initializes a new symbol table.

        Args:
            parent: The parent symbol table (optional). If None, this is the global scope.
        """
        self.symbols: Dict[str, Any] = {}
        self.parent: Optional['SymbolTable'] = parent

    def define(self, name: str, value: Any) -> None:
        """
        Defines a new symbol in the current scope.

        Args:
            name: The name of the symbol.
            value: The value of the symbol.
        """
        self.symbols[name] = value

    def resolve(self, name: str) -> Optional[Any]:
        """
        Resolves a symbol by searching the current scope and its parent scopes.

        Args:
            name: The name of the symbol to resolve.

        Returns:
            The value of the symbol if found, otherwise None.
        """
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.resolve(name)
        return None

    def assign(self, name: str, value: Any) -> bool:
        """
        Assigns a new value to an existing symbol.  Searches up the scope chain.

        Args:
            name: The name of the symbol to assign.
            value: The new value of the symbol.

        Returns:
            True if the assignment was successful, False if the symbol was not found.
        """
        if name in self.symbols:
            self.symbols[name] = value
            return True
        if self.parent:
            return self.parent.assign(name, value)
        return False

    def __repr__(self) -> str:
        return f"SymbolTable(symbols={self.symbols}, parent={self.parent})"


class TestSymbolTable(unittest.TestCase):
    """
    Unit tests for the SymbolTable class.
    """

    def test_define_and_resolve(self):
        """
        Tests defining a symbol and resolving it in the same scope.
        """
        table = SymbolTable()
        table.define("x", 10)
        self.assertEqual(table.resolve("x"), 10)

    def test_resolve_nonexistent(self):
        """
        Tests resolving a symbol that does not exist.
        """
        table = SymbolTable()
        self.assertIsNone(table.resolve("y"))

    def test_nested_scopes(self):
        """
        Tests defining and resolving symbols in nested scopes.
        """
        global_table = SymbolTable()
        global_table.define("global_var", 100)

        local_table = SymbolTable(parent=global_table)
        local_table.define("local_var", 200)

        self.assertEqual(local_table.resolve("local_var"), 200)
        self.assertEqual(local_table.resolve("global_var"), 100)
        self.assertIsNone(local_table.resolve("nonexistent_var"))

        self.assertEqual(global_table.resolve("global_var"), 100)
        self.assertIsNone(global_table.resolve("local_var"))

    def test_shadowing(self):
        """
        Tests shadowing a symbol in a nested scope.
        """
        global_table = SymbolTable()
        global_table.define("x", 10)

        local_table = SymbolTable(parent=global_table)
        local_table.define("x", 20)

        self.assertEqual(local_table.resolve("x"), 20)
        self.assertEqual(global_table.resolve("x"), 10)

    def test_assign_existing(self):
        """
        Tests assigning a new value to an existing symbol.
        """
        table = SymbolTable()
        table.define("x", 10)
        self.assertTrue(table.assign("x", 30))
        self.assertEqual(table.resolve("x"), 30)

    def test_assign_nonexistent(self):
        """
        Tests assigning a value to a symbol that does not exist.
        """
        table = SymbolTable()
        self.assertFalse(table.assign("y", 40))
        self.assertIsNone(table.resolve("y"))

    def test_assign_nested_scopes(self):
        """
        Tests assigning a value to a symbol in nested scopes.
        """
        global_table = SymbolTable()
        global_table.define("x", 10)

        local_table = SymbolTable(parent=global_table)
        local_table.define("y", 20)

        self.assertTrue(local_table.assign("x", 30))
        self.assertEqual(local_table.resolve("x"), 30)
        self.assertEqual(global_table.resolve("x"), 30)  # Global table is also updated

        self.assertTrue(local_table.assign("y", 40))
        self.assertEqual(local_table.resolve("y"), 40)

        self.assertFalse(local_table.assign("z", 50))
        self.assertIsNone(local_table.resolve("z"))
        self.assertIsNone(global_table.resolve("z"))

    def test_assign_to_global_from_local(self):
        global_table = SymbolTable()
        global_table.define("x", 10)

        local_table = SymbolTable(parent=global_table)
        self.assertTrue(local_table.assign("x", 20))
        self.assertEqual(global_table.resolve("x"), 20)
        self.assertEqual(local_table.resolve("x"), 20)

    def test_multiple_nested_scopes(self):
        global_table = SymbolTable()
        global_table.define("x", 10)

        mid_table = SymbolTable(parent=global_table)
        mid_table.define("y", 20)

        local_table = SymbolTable(parent=mid_table)
        local_table.define("z", 30)

        self.assertEqual(local_table.resolve("x"), 10)
        self.assertEqual(local_table.resolve("y"), 20)
        self.assertEqual(local_table.resolve("z"), 30)

        self.assertEqual(mid_table.resolve("x"), 10)
        self.assertEqual(mid_table.resolve("y"), 20)
        self.assertIsNone(mid_table.resolve("z"))

        self.assertEqual(global_table.resolve("x"), 10)
        self.assertIsNone(global_table.resolve("y"))
        self.assertIsNone(global_table.resolve("z"))

        self.assertTrue(local_table.assign("x", 40))
        self.assertEqual(global_table.resolve("x"), 40)
        self.assertEqual(mid_table.resolve("x"), 40)
        self.assertEqual(local_table.resolve("x"), 40)

if __name__ == '__main__':
    unittest.main()