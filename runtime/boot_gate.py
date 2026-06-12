from runtime.contract_registry import RuntimeContractRegistry, run_contract_gate_or_exit


def boot_gate(registry: RuntimeContractRegistry):
    return run_contract_gate_or_exit(registry)