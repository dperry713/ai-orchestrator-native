from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class RuntimeContract:
    name: str
    retries: int = 2
    timeout: float = 30.0
    critical: bool = False


class RuntimeContractRegistry:
    def __init__(self):
        self._contracts: Dict[str, RuntimeContract] = {}

    def register(self, contract: RuntimeContract):
        self._contracts[contract.name] = contract

    def get(self, name: str) -> Optional[RuntimeContract]:
        return self._contracts.get(name)

    def all(self):
        return list(self._contracts.values())


def run_contract_gate_or_exit(registry: RuntimeContractRegistry):
    if not registry._contracts:
        raise SystemExit("BOOT FAILED: no runtime contracts registered")
    return True