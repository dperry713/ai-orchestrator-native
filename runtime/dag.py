import asyncio
from collections import defaultdict, deque
from typing import Any, Callable, Dict, List


class DAGOrchestrator:
    def __init__(self):
        self.nodes: Dict[str, Callable[..., Any]] = {}
        self.edges: Dict[str, List[str]] = defaultdict(list)

    def add_node(self, name: str, fn: Callable[..., Any]):
        self.nodes[name] = fn

    def add_edge(self, src: str, dst: str):
        self.edges[src].append(dst)

    def _toposort(self):
        indeg = {n: 0 for n in self.nodes}
        for src, dsts in self.edges.items():
            for d in dsts:
                indeg[d] += 1

                q = deque([n for n in self.nodes if indeg[n] == 0])
                order = []

                while q:
                    node = q.popleft()
                    order.append(node)

                    for nxt in self.edges[node]:
                        indeg[nxt] -= 1
                        if indeg[nxt] == 0:
                            q.append(nxt)

                            if len(order) != len(self.nodes):
                                raise RuntimeError("DAG cycle detected")

                            return order

    async def run(self, *args, **kwargs):
        order = self._toposort()
        results = {}

        for node in order:
            fn = self.nodes[node]
            if asyncio.iscoroutinefunction(fn):
                results[node] = await fn(results, *args, **kwargs)
            else:
                results[node] = fn(results, *args, **kwargs)

                return results