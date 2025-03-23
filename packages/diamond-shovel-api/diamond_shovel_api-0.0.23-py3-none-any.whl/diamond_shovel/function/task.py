from typing import Callable, Coroutine, Any, AsyncIterator

from diamond_shovel.plugins import PluginInitContext


class Company:
    company_name: str
    assets: list['Asset']

    def __init__(self, company_name: str):
        ...

class Asset:
    owner: Company
    host: str
    port: int

    layer4_protocol: int # eg. socket.IPPROTO_TCP

    identified_service: str
    signature: str

    discovered_techniques: list[str]
    vulnerabilities: list['Vulnerability']

    def __init__(self, owner: Company, host: str, port: int, layer4_protocol: int):
        ...

class Vulnerability:
    name: str
    description: str
    severity: str
    references: list[str]

    def __init__(self, name: str, description: str, severity: str, references: list[str]):
        ...

class TaskContext:
    async def get_worker_result(self, plugin_name, worker_name):
        ...

    async def get_remaining_workers(self) -> list[str]:
        ...

    async def get(self, item):
        ...

    async def set(self, key, value):
        ...

    def collect(self, key: str, size: int = 10) -> AsyncIterator[Any]:
        ...

    def __getitem__(self, item):
        ...

    def __setitem__(self, key, value):
        ...

    def operate(self, key, func, *args, **kwargs):
        ...

    def put_company(self, company: Company):
        ...

    def find_discovered_asset(self, host: str, port: int, layer4_proto: int) -> Asset:
        ...

    def put_relation(self, company: Company, target: Any, weight: float):
        ...

    def find_by_target(self, target: Any) -> list[tuple[Company, float]]:
        ...

    def get_relation_weight(self, company: Company, target: Any) -> float:
        ...


class WorkerPool:
    def register_worker(self, plugin_ctx: PluginInitContext, worker: Callable[[TaskContext], Coroutine[Any, Any, Any]], nice: int = 0):
        ...

pools: dict[str, WorkerPool] = {}
