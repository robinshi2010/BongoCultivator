from enum import Enum

class PetState(Enum):
    IDLE = 0      # 闭关/打坐 (Low APM)
    COMBAT = 1    # 历练/施法 (High APM)
    # 可以扩展：WALK, SLEEP, ASCEND (渡劫)
