from dataclasses import dataclass
from typing import Optional, List, Dict
import multiprocessing
import logging
from datetime import datetime

@dataclass
class TrialsConfig:
    iterations: int = 2000
    trials: int = 5