
from typing import Dict
from threading import Lock

class EndpointRegistry:
    def __init__(self):
        self._registry: Dict[str, Dict] = {}
        self._lock = Lock()

    def add(self, name: str, config: Dict):
        with self._lock:
            self._registry[name] = config

    def update(self, name: str, config: Dict):
        with self._lock:
            if name in self._registry:
                self._registry[name].update(config)

    def delete(self, name: str):
        with self._lock:
            self._registry.pop(name, None)

    def get(self, name: str) -> Dict:
        return self._registry.get(name, {})

    def list_all(self) -> Dict[str, Dict]:
        return self._registry.copy()
