import asyncio
import traceback
from typing import Callable


class Supervisor:
    def __init__(self, runner: Callable):
        self.runner = runner
        self.failures = 0
        self.max_failures = 3

    async def run_forever(self):
        while True:
            try:
                await self.runner()
                self.failures = 0

            except Exception as e:
                self.failures += 1
                print("SUPERVISOR ERROR:", str(e))
                print(traceback.format_exc())

                if self.failures >= self.max_failures:
                    print("SUPERVISOR SHUTDOWN: too many failures")
                    return

                await asyncio.sleep(1)