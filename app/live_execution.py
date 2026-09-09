from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any

from .execution import execute_production_brief


@dataclass
class LiveRun:
    execution_id: str
    brief: str
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    status: str = "PENDING"
    error: str | None = None
    task: asyncio.Task | None = None
    snapshot: dict[str, Any] = field(default_factory=dict)


class LiveExecutionManager:
    def __init__(self):
        self.runs: dict[str, LiveRun] = {}

    def create(self, brief: str) -> LiveRun:
        run = LiveRun(str(uuid.uuid4()), brief)
        self.runs[run.execution_id] = run
        return run

    async def start(self, run: LiveRun) -> None:
        run.status = "RUNNING"
        run.task = asyncio.create_task(self._execute(run))

    async def _publish(self, run: LiveRun, event_type: str, **data: Any) -> None:
        await run.queue.put({"type": event_type, "execution_id": run.execution_id, **data})

    async def _execute(self, run: LiveRun) -> None:
        try:
            await self._publish(run, "execution_started", status="RUNNING", brief=run.brief)
            trace, events = await asyncio.wait_for(
                execute_production_brief(run.brief),
                timeout=150,
            )
            run.snapshot = trace.snapshot()
            for item in events:
                if item.get("author"):
                    await self._publish(
                        run,
                        "agent_event",
                        agent=item["author"],
                        status="COMPLETED",
                        text=str(item.get("text", ""))[-1200:],
                    )
                if item.get("error"):
                    await self._publish(
                        run,
                        "error",
                        message=item["error"],
                        details=item.get("details"),
                    )
            run.status = trace.status
            await self._publish(run, "execution_snapshot", snapshot=run.snapshot)
            await self._publish(run, "execution_completed", status=run.status, snapshot=run.snapshot)
        except asyncio.TimeoutError:
            run.status = "FAILED"
            run.error = "Agent execution timed out after 150 seconds."
            await self._publish(run, "error", message=run.error)
            await self._publish(run, "execution_completed", status="FAILED")
        except Exception as exc:
            run.status = "FAILED"
            run.error = str(exc)
            await self._publish(run, "error", message=run.error)
            await self._publish(run, "execution_completed", status="FAILED")
        finally:
            await run.queue.put(None)


manager = LiveExecutionManager()
