"""Strike 1a structural checks on the harness package (U87 / §5.1 / §4.3 item 2; §2.2).

No binary floating point, no decimal module and no clock in the decision modules; no network or
order capability anywhere in the Strike 1a package. Static AST checks: they show what the source
contains, not what a running process could do (Branch C, §2.3)."""
import ast
import os
import unittest

PKG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sl_pt_001")
MODULES = ["exact.py", "decide.py", "validate.py"]
FORBIDDEN_IMPORTS = {"decimal", "time", "datetime", "socket", "ssl", "http", "urllib", "requests",
                     "subprocess", "os", "random", "secrets", "ctypes", "asyncio"}
FORBIDDEN_NAMES = {"float", "eval", "exec", "__import__", "open", "input"}


def trees():
    for name in MODULES:
        with open(os.path.join(PKG, name), encoding="utf-8") as fh:
            yield name, ast.parse(fh.read(), filename=name)


class Purity(unittest.TestCase):
    def test_U87_no_float_literal_or_call(self):
        for name, tree in trees():
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, (float, complex)):
                    self.fail(f"{name}:{node.lineno} float/complex literal")
                if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
                    self.fail(f"{name}:{node.lineno} forbidden name {node.id}")

    def test_U87_no_true_division_by_or_of_an_int_literal(self):
        # int / int yields a float in Python; the package never divides by or into a bare int literal.
        for name, tree in trees():
            for node in ast.walk(tree):
                if isinstance(node, (ast.BinOp, ast.AugAssign)) and isinstance(node.op, ast.Div):
                    sides = (node.left, node.right) if isinstance(node, ast.BinOp) else (node.value,)
                    for side in sides:
                        self.assertFalse(isinstance(side, ast.Constant) and isinstance(side.value, int),
                                         f"{name}:{node.lineno} '/' with a bare int literal")

    def test_boundary_no_forbidden_imports(self):
        for name, tree in trees():
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods = {a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom):
                    mods = {(node.module or "").split(".")[0]}
                else:
                    continue
                bad = mods & FORBIDDEN_IMPORTS
                self.assertFalse(bad, f"{name}:{node.lineno} imports {bad}")

    def test_X10_no_order_vocabulary_in_package(self):
        # Static evidence that Strike 1a contains no submit / cancel / account code path (§2.2).
        for fname in os.listdir(PKG):
            if fname.endswith(".py"):
                with open(os.path.join(PKG, fname), encoding="utf-8") as fh:
                    src = fh.read().lower()
                for word in ("/v2/orders", "paper-api", "api.alpaca.markets", "apca-api-key", "submit_order",
                             "cancel_order", "/v2/account"):
                    self.assertNotIn(word, src, f"{fname} contains {word!r}")


class EvidenceModuleBoundary(unittest.TestCase):
    """evidence.py writes files (artifacts, chain) by design; it must still have no network or order capability."""

    def test_evidence_no_network_imports(self):
        for fname in ("evidence.py", "controller.py"):                 # controller.py (Strike 3): market I/O injected
            with open(os.path.join(PKG, fname), encoding="utf-8") as fh:
                src = fh.read()
            tree = ast.parse(src)
            net = {"socket", "ssl", "http", "urllib", "requests", "asyncio", "subprocess", "ctypes"}
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    mods = {a.name.split(".")[0] for a in node.names} if isinstance(node, ast.Import) else {(node.module or "").split(".")[0]}
                    self.assertFalse(mods & net, f"{fname} imports {mods & net}")
            for word in ("/v2/orders", "paper-api", "api.alpaca.markets", "submit_order", "cancel_order", "/v2/account"):
                self.assertNotIn(word, src, f"{fname} contains {word!r}")


if __name__ == "__main__":
    unittest.main()
