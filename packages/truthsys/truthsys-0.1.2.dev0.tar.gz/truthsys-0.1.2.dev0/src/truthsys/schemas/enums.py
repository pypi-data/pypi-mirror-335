from enum import Enum


class PredictionEnum(str, Enum):
    supports = "SUPPORTS"
    not_enough_info = "NOT ENOUGH INFO"
    refutes = "REFUTES"

    @classmethod
    def from_num(cls, num: "PredictionNumEnum") -> "PredictionEnum":
        match num:
            case PredictionNumEnum.supports:
                return cls.supports
            case PredictionNumEnum.not_enough_info:
                return cls.not_enough_info
            case PredictionNumEnum.refutes:
                return cls.refutes


class PredictionNumEnum(int, Enum):
    refutes = 0
    not_enough_info = 1
    supports = 2

    @classmethod
    def from_str(cls, string: "PredictionEnum") -> "PredictionNumEnum":
        match string:
            case PredictionEnum.supports:
                return cls.supports
            case PredictionEnum.not_enough_info:
                return cls.not_enough_info
            case PredictionEnum.refutes:
                return cls.refutes
