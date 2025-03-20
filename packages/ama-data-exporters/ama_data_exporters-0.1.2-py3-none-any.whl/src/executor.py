import asyncio
from typing import Any, List, Coroutine, Tuple

class AsyncExecutor:
    def __init__(self):
        """Initialize the AsyncExecutor"""
        self.tasks: List[Tuple[Coroutine, Tuple, dict]] = []

    def submit_task(self, coroutine: Coroutine, *args, **kwargs):
        """Submit an async coroutine as a task."""
        self.tasks.append((coroutine, args, kwargs))

    async def run(self) -> List[Any]:
        """Run multiple functions asynchronously in parallel."""
        results = []
        if not self.tasks:
            return results

        async with asyncio.TaskGroup() as tg:
            tasks = []
            for func, args, kwargs in self.tasks:
                if asyncio.iscoroutinefunction(func):
                    task = tg.create_task(func(*args, **kwargs))
                else:
                    task = tg.create_task(asyncio.to_thread(func, *args, **kwargs))
                tasks.append(task)
        # Collect results from completed tasks
        results = [task.result() for task in tasks]

        # Clear the task queue after execution
        self.tasks.clear()

        return results

# Example usage with a sync function
def sync_sample_task(i):
    print(f"Sync Task {i} started")
    import time
    time.sleep(5)
    print(f"Sync Task {i} completed")
    return f"Sync Task {i} result"

# Example usage with an async function
async def async_sample_task(n: int):
    print(f"Async Task {n} started")
    await asyncio.sleep(5)
    print(f"Async Task {n} completed")
    return f"Async Task {n} result"

async def main():
    executor = AsyncExecutor()

    # Submit async tasks
    for i in range(5):
        executor.submit_task(async_sample_task, i)

    # Submit sync tasks
    for i in range(5):
        executor.submit_task(sync_sample_task, i)

    # Run all submitted tasks
    results = await executor.run()
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
