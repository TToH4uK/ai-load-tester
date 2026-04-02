from pydantic import BaseModel
from typing import List, Optional, Tuple, Union

class ValidateRules(BaseModel):
    intent: Optional[str] = None
    contains: Optional[List[str]] = None
    min_similarity: Optional[float] = 0.7

class Step(BaseModel):
    id: str
    # Union позволяет использовать и строку, и список строк в YAML
    user_say: Union[str, List[str]] 
    validation: Optional[ValidateRules] = None
    on_success: str
    on_fail: str

class ScenarioConfig(BaseModel):
    base_url: str
    timeout: float = 5.0
    typing_delay: Tuple[int, int] = (1, 3)

class Scenario(BaseModel):
    name: str
    config: ScenarioConfig
    steps: List[Step]