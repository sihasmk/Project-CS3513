from enum import Enum, auto


class NodeType(Enum):
    let = auto()
    fcn_form = auto()
    identifier = auto()
    integer = auto()
    string = auto()
    where = auto()
    gamma = auto()
    # 'lambda' is a reserved keyword in Python, so we have used a trailing underscore
    lambda_ = auto()
    tau = auto()
    rec = auto()
    aug = auto()
    conditional = auto()
    op_or = auto()
    op_and = auto()
    op_not = auto()
    op_compare = auto()
    op_plus = auto()
    op_minus = auto()
    op_neg = auto()
    op_mul = auto()
    op_div = auto()
    op_pow = auto()
    at = auto()
    true_value = auto()
    false_value = auto()
    nil = auto()
    dummy = auto()
    within = auto()
    # 'and' is a reserved keyword in Python, so we have used a trailing underscore
    and_ = auto()
    equal = auto()
    comma = auto()
    empty_params = auto()

    def __str__(self) -> str:
        return super().__str__()
