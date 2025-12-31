# core/model.py

class NeutrosophicZNumber:
    """
    NZN = [(αA, αC), (βA, βC), (γA, γC)]
    """

    def __init__(self, aA, aC, bA, bC, gA, gC):
        self.aA = aA
        self.aC = aC
        self.bA = bA
        self.bC = bC
        self.gA = gA
        self.gC = gC

    def is_valid(self) -> bool:
        return (
            0 <= self.aA <= 1 and 0 <= self.aC <= 1 and
            0 <= self.bA <= 1 and 0 <= self.bC <= 1 and
            0 <= self.gA <= 1 and 0 <= self.gC <= 1
        )

    def __str__(self):
        return (
            f"[({self.aA:.4f};{self.aC:.4f});"
            f"({self.bA:.4f};{self.bC:.4f});"
            f"({self.gA:.4f};{self.gC:.4f})]"
        )

