from pydantic import BaseModel
from datetime import datetime

class Veiculo(BaseModel):
    id: int
    name: str
    team: str
    front_left: float
    front_right: float
    rear_left: float
    rear_right: float
    position: float
    timestamp: float
