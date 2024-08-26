from attr import frozen


@frozen
class Edge:
    source: str
    target: str

    def to_string(self) -> str:
        return f"({self.source} -> {self.target})"
