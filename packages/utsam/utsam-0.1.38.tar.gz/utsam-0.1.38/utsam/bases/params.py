from dataclasses import dataclass

@dataclass
class SemesterParams():
    spring: str = "SPR" 
    autumn: str = "AUT"

_SELECT_ = 'Select'

_CACHE_ = 'cache'
_LOGS_ = 'logs'
_METADATA_ = 'metadata'

ZSCORE_COL = 'zscore'