# AwaitList

**AwaitList** is an asynchronous task scheduler for Python. It allows you to manage and wait for tasks based on their scheduled execution times using Python's `asyncio` framework. It is designed to perform long polling-like behavior locally.

## Features

- **Time-based Task Scheduling**: Add tasks with a specific execution time by `add_task()`, and user can wait for the task by `wait_for_next_task()`.
- **User-controlled Execution**: Tasks are not automatically executed when their scheduled time arrives. Instead, users control the execution by iterating through tasks using `async for`, allowing flexibility to integrate the task execution into custom workflows.
- **Dynamic Task Management**: Add tasks dynamically at runtime.

## Installation

```bash
pip install awaitlist
```

## Usage

### Example: Scheduling and Executing Tasks

Here’s a basic example of how to use `AwaitList` to schedule tasks and wait for their execution times.

#### Code
[sample.py](sample.py)
```python
import asyncio
from datetime import datetime, timedelta

from awaitlist import AwaitList


async def process_tasks(await_list: AwaitList):
    """Fetch tasks from the list and process them sequentially."""
    async for task_time, task_name in await_list.wait_for_next_task():
        print(f"[Processor] Executing: {task_name} at {datetime.now()}")


async def add_tasks(await_list: AwaitList):
    """Example of dynamically adding tasks."""
    now = datetime.now()
    print(f"[AddTasks] Current time: {now}")

    # Add a task scheduled 5 second later
    task_time_5min = now + timedelta(seconds=5)
    await await_list.add_task(task_time_5min, "Task 5 second later")
    print(f"[AddTasks] Added: Task 5 second later for {task_time_5min}")

    await asyncio.sleep(1)  # Wait 1 second

    # Add a task scheduled 1 second later
    task_time_1sec = now + timedelta(seconds=1)
    await await_list.add_task(task_time_1sec, "Task 1 second later")
    print(f"[AddTasks] Added: Task 1 second later for {task_time_1sec}")


async def main():
    await_list = AwaitList()
    await asyncio.gather(process_tasks(await_list), add_tasks(await_list))


# Execute
if __name__ == "__main__":
    asyncio.run(main())
```

#### Output

```
[AddTasks] Current time: 2025-01-21 01:52:45.588777
[AddTasks] Added: Task 5 second later for 2025-01-21 01:52:50.588777
[AddTasks] Added: Task 1 second later for 2025-01-21 01:52:46.588777
[Processor] Executing: Task 1 second later at 2025-01-21 01:52:46.591487
[Processor] Executing: Task 5 second later at 2025-01-21 01:52:50.593209
```

## API Reference

### `AwaitList`

#### Methods

1. **`add_task(task_time: datetime, task_name: str)`**
   - Add a task to the queue.
   - **Args**:
     - `task_time (datetime)`: The scheduled time for the task.
     - `task_name (str)`: The name of the task.
   - **Returns**:
     - `task_id (uuid.UUID)`: The ID of the task.

2. **`cancel_task(task_name: str)`**
   - Cancel a task from the queue.
   - **Args**:
     - `task_id (uuid.UUID)`: The ID of the task to cancel.

3. **`wait_for_next_task() -> AsyncGenerator[Tuple[datetime, str], None]`**
   - Wait for the next task in the queue.
   - Yields the `datetime` and `name` of the next scheduled task.

## Use Cases

- Delayed or deferred task execution where tasks are processed only when the user determines they are ready.
- Event-driven applications with precise timing needs, where tasks are scheduled but not automatically executed until iterated.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.

