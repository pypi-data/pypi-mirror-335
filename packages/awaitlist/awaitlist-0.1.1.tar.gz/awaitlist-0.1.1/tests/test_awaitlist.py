from datetime import datetime, timedelta

import pytest

from awaitlist.awaitlist import AwaitList


@pytest.mark.asyncio
async def test_add_and_wait_for_next_task():
    await_list = AwaitList()

    # Add tasks based on the current time
    now = datetime.now()
    task1_time = now + timedelta(seconds=1)
    task2_time = now + timedelta(seconds=2)

    await await_list.add_task(task1_time, "task1")
    await await_list.add_task(task2_time, "task2")

    # Ensure tasks are processed in the correct order
    async for task_time, task_name in await_list.wait_for_next_task():
        if task_name == "task1":
            assert task_time == task1_time
        elif task_name == "task2":
            assert task_time == task2_time
            break  # Exit the loop after verifying all tasks


@pytest.mark.asyncio
async def test_dynamic_task_addition():
    await_list = AwaitList()

    # Add tasks based on the current time
    now = datetime.now()
    task_time_2sec = now + timedelta(seconds=2)
    task_time_1sec = now + timedelta(seconds=1)

    # Add a task scheduled 2 seconds later
    await await_list.add_task(task_time_2sec, "Task 2 second later")
    # Add a task scheduled 1 second later
    await await_list.add_task(task_time_1sec, "Task 1 second later")

    # Ensure tasks are processed in the correct order
    tasks_processed = []
    async for task_time, task_name in await_list.wait_for_next_task():
        tasks_processed.append((task_time, task_name))
        if len(tasks_processed) == 2:
            break  # Exit the loop after verifying all tasks

    # Verify that tasks are processed in the correct order
    assert tasks_processed[0][1] == "Task 1 second later"
    assert tasks_processed[1][1] == "Task 2 second later"


@pytest.mark.asyncio
async def test_cancel_task():
    await_list = AwaitList()

    # Add tasks based on the current time
    now = datetime.now()
    task1_time = now + timedelta(seconds=1)
    task2_time = now + timedelta(seconds=2)

    # Add tasks and get their IDs
    task1_id = await await_list.add_task(task1_time, "task1")
    _ = await await_list.add_task(task2_time, "task2")

    # Cancel task1
    cancel_result = await await_list.cancel_task(task1_id)
    assert cancel_result is True  # Verify that the cancellation was successful

    # Ensure tasks are processed in the correct order
    tasks_processed = []
    async for task_time, task_name in await_list.wait_for_next_task():
        tasks_processed.append((task_time, task_name))
        if len(tasks_processed) == 1:
            break  # Exit the loop after verifying all tasks

    # Verify that task1 is cancelled and only task2 is processed
    assert len(tasks_processed) == 1
    assert tasks_processed[0][1] == "task2"
