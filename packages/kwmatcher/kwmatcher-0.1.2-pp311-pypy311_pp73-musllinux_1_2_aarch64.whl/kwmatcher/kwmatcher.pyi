from typing import Set

class AhoMatcher:
    def __init__(self, use_logic: bool = True) -> None: ...
    def build(self, patterns: Set[str]) -> None: ...
    def find(self, haystack: str) -> Set[str]: ...
