from operator import eq, ge, gt, le, lt, ne


class OperatorFunction:
    operator_functions = {
        "gt": gt,
        "gte": ge,
        "lt": lt,
        "lte": le,
        "exact": eq,
        "ne": ne,
    }

    def __init__(self, operator):
        if operator not in self.operator_functions:
            raise ValueError(f"Unsupported operator: {operator}")
        self.function = self.operator_functions[operator]

    def __call__(self, a, b):
        return self.function(a, b)
