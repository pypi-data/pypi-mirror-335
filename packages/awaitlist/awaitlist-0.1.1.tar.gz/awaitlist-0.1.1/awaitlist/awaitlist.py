import asyncio
import uuid
from datetime import datetime
from typing import AsyncGenerator


class AwaitList:
    """
    Asynchronous task scheduler that waits for the execution time of tasks.
    Provides a mechanism to process tasks sequentially based on time.
    """

    def __init__(self):
        # Task list [(execution time, task ID, task name)]
        self.tasks: list[tuple[datetime, uuid.UUID, str]] = []
        # For task notification
        self.condition = asyncio.Condition()

    async def add_task(self, task_time: datetime, task_name: str) -> uuid.UUID:
        """
        Add a new task and return a task ID for cancellation.

        Args:
            task_time (datetime): Scheduled execution time.
            task_name (str): Task name.

        Returns:
            uuid.UUID: Task ID that can be used to cancel the task.
        """
        async with self.condition:
            task_id = uuid.uuid4()
            self.tasks.append((task_time, task_id, task_name))
            self.tasks.sort(key=lambda x: x[0])  # Sort tasks by time
            self.condition.notify_all()  # Notify waiting processes
            return task_id

    async def cancel_task(self, task_id: uuid.UUID) -> bool:
        """
        Cancel a task by its ID.

        Args:
            task_id (uuid.UUID): The ID of the task to cancel.

        Returns:
            bool: True if the task was successfully cancelled, False otherwise.
        """
        async with self.condition:
            for i, (_, t_id, _) in enumerate(self.tasks):
                if t_id == task_id:
                    del self.tasks[i]
                    self.condition.notify_all()
                    return True
            return False

    async def wait_for_next_task(self) -> AsyncGenerator[tuple[datetime, str], None]:
        """
        Wait for the next task and yield it sequentially.

        Yields:
            Tuple[datetime, str]: Execution time and task name.
        """
        while True:
            async with self.condition:  # Ensure the lock is acquired
                if self.tasks:
                    now = datetime.now()
                    next_task_time, _, next_task_name = self.tasks[0]

                    # If the next task is ready to execute
                    if next_task_time <= now:
                        self.tasks.pop(0)  # Remove from the list
                        yield next_task_time, next_task_name
                        continue

                    # Wait until the next task time
                    sleep_time = (next_task_time - now).total_seconds()
                else:
                    # If there are no tasks, wait indefinitely
                    sleep_time = None

            try:
                if sleep_time is not None and sleep_time > 0:
                    # Wait for either a timeout or a new task notification
                    async with self.condition:
                        await asyncio.wait_for(
                            self.condition.wait(), timeout=sleep_time
                        )
                else:
                    # Wait indefinitely for a new task notification
                    async with self.condition:
                        await self.condition.wait()
            except asyncio.TimeoutError:
                pass  # Timeout occurred, recheck the task list
