from attr import frozen


@frozen
class Edge:
    source: int
    target: int

    def to_string(self) -> str:
        return f"({self.source} -> {self.target})"
