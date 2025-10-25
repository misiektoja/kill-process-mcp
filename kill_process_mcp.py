"""
Author: Michal Szymanski <misiektoja-github@rm-rf.ninja>
v1.0

Cross-platform MCP server exposing tools to list and kill OS processes:
https://github.com/misiektoja/kill-process-mcp

MCP tools:
- process_list(): List running processes with optional filtering, sorting and limit
- process_kill(): Kill the selected process
"""


from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Literal

import sys
import os
if sys.platform == "win32":
    SYSTEM_USERS = {"SYSTEM", "NT AUTHORITY\\SYSTEM", "LocalService", "NetworkService"}
else:
    SYSTEM_USERS = {"root"}

import ctypes
import ctypes.util


# Cross-platform stub, overridden on macOS
def _phys_footprint(pid: int) -> int:
    return 0


# macOS-only helper for Activity Monitor-style memory
if sys.platform == "darwin":
    _RUSAGE_INFO_V6 = 2

    class _RUsageInfoV6(ctypes.Structure):
        _fields_ = [("ri_uuid", ctypes.c_uint8 * 16),
                    ("ri_user_time", ctypes.c_uint64),
                    ("ri_system_time", ctypes.c_uint64),
                    ("ri_pkg_idle_wkups", ctypes.c_uint64),
                    ("ri_interrupt_wkups", ctypes.c_uint64),
                    ("ri_pageins", ctypes.c_uint64),
                    ("ri_wired_size", ctypes.c_uint64),
                    ("ri_resident_size", ctypes.c_uint64),
                    ("ri_phys_footprint", ctypes.c_uint64),
                    ("ri_proc_start_abstime", ctypes.c_uint64),
                    ("ri_proc_exit_abstime", ctypes.c_uint64),
                    ("ri_child_user_time", ctypes.c_uint64),
                    ("ri_child_system_time", ctypes.c_uint64),
                    ("ri_child_pkg_idle_wkups", ctypes.c_uint64),
                    ("ri_child_interrupt_wkups", ctypes.c_uint64),
                    ("ri_child_pageins", ctypes.c_uint64),
                    ("ri_child_elapsed_abstime", ctypes.c_uint64)]
    _libproc = ctypes.CDLL(ctypes.util.find_library("proc"), use_errno=True)
    _proc_pid_rusage = _libproc.proc_pid_rusage
    _proc_pid_rusage.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(_RUsageInfoV6)]
    _proc_pid_rusage.restype = ctypes.c_int

    def _phys_footprint(pid: int) -> int:
        info = _RUsageInfoV6()
        try:
            if _proc_pid_rusage(pid, _RUSAGE_INFO_V6, ctypes.byref(info)) == 0:
                return info.ri_phys_footprint
        except Exception:
            pass
        return 0

import psutil
from mcp.server.fastmcp import Context, FastMCP


mcp = FastMCP("kill_process_mcp", "MCP server exposing tools to list and kill OS processes", auth_server_provider=None, auth=None)


# Prepares per-process CPU counters and returns initial sample
def _snapshot_cpu() -> Dict[int, float]:
    data: Dict[int, float] = {}
    for proc in psutil.process_iter(attrs=["pid"]):
        try:
            data[proc.pid] = proc.cpu_percent(None)
        except psutil.Error:
            continue
    return data


# Retrieves a safe list of process handles
def _collect_processes() -> List[psutil.Process]:
    procs: List[psutil.Process] = []
    for proc in psutil.process_iter(attrs=["pid", "username"]):
        try:
            procs.append(proc)
        except psutil.Error:
            continue
    return procs


# Converts a psutil.Process to a JSON-serialisable dict
def _serialize(proc: psutil.Process) -> Dict[str, Any]:
    try:
        try:
            mem = _phys_footprint(proc.pid)
        except Exception:
            mem = 0
        if not mem:
            try:
                mi = proc.memory_full_info()
                mem = getattr(mi, "uss", mi.rss)
            except Exception:
                try:
                    mem = proc.memory_info().rss
                except Exception:
                    mem = 0

        if sys.platform == "win32":
            try:
                exe_name = os.path.basename(proc.exe())
                name = exe_name if exe_name else proc.name()
            except (psutil.Error, OSError, FileNotFoundError):
                name = proc.name()
        else:
            try:
                name = proc.name()
            except psutil.Error:
                name = "<unknown>"

        cpu = proc.cpu_percent(None)
        return {"pid": proc.pid, "name": name, "username": proc.username(), "status": proc.status(), "cpu_percent": cpu, "rss": mem}
    except psutil.Error:
        return {"pid": proc.pid, "name": "<terminated>", "username": "<unknown>", "status": "<terminated>", "cpu_percent": 0.0, "rss": 0}


@mcp.tool()
async def process_list(sort_by: Literal["cpu", "memory"] = "cpu", duration: int = 2, limit: int | None = None, name_filter: str | None = None, user_filter: str | None = None, status_filter: Literal["running", "sleeping", "stopped", "zombie"] | None = None, min_cpu: float | None = None, min_memory: int | None = None, include_system: bool = False, sort_asc: bool = False, ctx: Context | None = None,) -> List[Dict[str, Any]]:
    """List running processes sorted by CPU or memory with optional name, user, status, CPU/memory thresholds, system-process filtering, sort order and limit."""

    if ctx:
        await ctx.info(
            f"process_list called sort_by={sort_by} duration={duration} "
            f"limit={limit} name_filter={name_filter} user_filter={user_filter} "
            f"status_filter={status_filter} min_cpu={min_cpu} min_memory={min_memory} "
            f"include_system={include_system} sort_asc={sort_asc}"
        )

    if sort_by not in {"cpu", "memory"}:
        raise ValueError("sort_by must be 'cpu' or 'memory'")

    if isinstance(limit, str):
        try:
            limit = int(limit)
        except ValueError:
            raise ValueError("limit must be an integer or null")

    _snapshot_cpu()

    if sort_by == "cpu":
        await asyncio.sleep(duration)
    else:
        await asyncio.sleep(0.1)

    procs = _collect_processes()
    serialised = [_serialize(p) for p in procs]

    if not include_system:
        serialised = [p for p in serialised if p["username"] not in SYSTEM_USERS]
    if name_filter is not None:
        serialised = [p for p in serialised if name_filter.lower() in p["name"].lower()]
    if user_filter is not None:
        serialised = [p for p in serialised if user_filter.lower() in p["username"].lower()]
    if status_filter is not None:
        serialised = [p for p in serialised if p["status"] == status_filter]
    if min_cpu is not None:
        serialised = [p for p in serialised if p["cpu_percent"] >= min_cpu]
    if min_memory is not None:
        serialised = [p for p in serialised if p["rss"] >= min_memory]

    key = "cpu_percent" if sort_by == "cpu" else "rss"
    result = sorted(serialised, key=lambda p: p[key], reverse=not sort_asc)

    if limit is not None:
        result = result[:limit]

    return result


@mcp.tool()
async def process_kill(pid: int, ctx: Context | None = None) -> str:
    """Kill the process identified by the given PID"""

    if ctx:
        await ctx.info(f"process_kill called pid={pid}")

    if pid == os.getpid():
        return "Refusing to kill MCP server process"

    try:
        proc = psutil.Process(pid)
        proc.kill()
        proc.wait(timeout=5)
        return f"Process {pid} terminated"
    except (psutil.NoSuchProcess, psutil.AccessDenied) as err:
        return f"Failed to kill {pid}: {err}"

if __name__ == "__main__":
    mcp.run()
