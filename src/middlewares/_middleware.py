from abc import ABC, abstractmethod
from typing import Any
from flask import Response

class Middleware(ABC):
	@abstractmethod
	async def process(self) -> Any:
		pass