from dataclasses import dataclass, field


@dataclass
class Member:
    id: str
    name: str
    direct_commission: float
    kickback_rate: float = 0.2
    children: list["Member"] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.id)

    def total_commission(self) -> float:
        children_commission = sum(child.total_commission() for child in self.children)
        kickback_commission = self.kickback_rate * children_commission
        return self.direct_commission + kickback_commission

    def print_commission(self, indent: int = 0):
        total = self.total_commission()
        children_commission = sum(child.total_commission() for child in self.children)
        kickback_commission = self.kickback_rate * children_commission

        indent_str = " " * indent * 4
        print(
            f"{indent_str}{self.name} ({total:.2f} = {self.direct_commission:.2f} + {kickback_commission:.2f})"
        )

        for child in self.children:
            child.print_commission(indent + 1)
