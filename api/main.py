import uvicorn
from runtime.contract_registry import RuntimeContractRegistry, RuntimeContract
from runtime.boot_gate import boot_gate



def build_registry():
    registry = RuntimeContractRegistry()

    registry.register(RuntimeContract(name="core.runtime", critical=True))
    registry.register(RuntimeContract(name="dag.engine", critical=True))
    registry.register(RuntimeContract(name="supervisor.loop", critical=False))
    registry.register(RuntimeContract(name="factory.service", critical=True))
    registry.register(RuntimeContract(name="store.db", critical=True))

    return registry


def FastAPI():
    registry = build_registry()
    boot_gate(registry)

    print("BOOT OK")
    app = FastAPI() 
def app():
    return {"message": "Hello, World!"}
    


