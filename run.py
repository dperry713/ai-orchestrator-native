import uvicorn
from runtime.contract_registry import RuntimeContractRegistry, RuntimeContract
from runtime.boot_gate import boot_gate


def build_registry():
    registry = RuntimeContractRegistry()

    registry.register(RuntimeContract(name="core.runtime", critical=True))
    registry.register(RuntimeContract(name="dag.engine", critical=True))
    registry.register(RuntimeContract(name="supervisor.loop", critical=False))

    return registry


def main():
    registry = build_registry()
    boot_gate(registry)

    print("BOOT OK")

    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()