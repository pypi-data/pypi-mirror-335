# -*- coding: utf-8 -*-
import logging
import os
import shlex
import shutil
import subprocess  # nosec
import threading
from typing import List, Literal, Tuple

import psutil
from chaoslib import decode_bytes
from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, Secrets

__all__ = [
    "with_normal_latency",
    "with_uniform_latency",
    "with_pareto_latency",
    "run_proxy",
    "stop_proxy",
]

logger = logging.getLogger("chaostoolkit")
lock = threading.Lock()

PROCS: dict[str, psutil.Process] = {}


def run_proxy(
    name: str, args: List[str], timeout: float = 60,
    set_http_proxy_variables: bool = False,
) -> Tuple[int, str, str]:
    """
    Run the lueur proxy with the given command line arguments. Use the
    name argument to track the started process, this can be used to call
    `stop_proxy` from a rollback action.

    Set `set_http_proxy_variables` so the HTTP_PROXY and HTTPS_PROXY
    environment variables of the process point at the started proxy.
    """
    lueur_path = shutil.which("lueur")
    if not lueur_path:
        raise ActivityFailed("lueur: not found")

    cmd = [lueur_path]
    cmd.extend(["--log-stdout", "run", "--no-ui"])
    cmd.extend(args)

    env = {}  # type: dict[str, str]
    stdout = stderr = b""
    try:
        logger.debug(f"Running lueur proxy: '{shlex.join(cmd)}'")
        p = psutil.Popen(  # nosec
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            shell=False,
        )

        with lock:
            PROCS[name] = p

        stdout, stderr = p.communicate(timeout=timeout)

        if set_http_proxy_variables:
            bound_proxy_addr = ""
            for c in p.net_connections("tcp4"):
                if c.status == "LISTEN":
                    addr = c.laddr
                    bound_proxy_addr = f"http://{addr[0]}:{addr[1]}"
                    break

            if bound_proxy_addr:
                os.putenv("HTTP_PROXY", bound_proxy_addr)
                os.putenv("HTTPS_PROXY", bound_proxy_addr)

    except KeyboardInterrupt:
        logger.debug(
            "Caught SIGINT signal while running load test. Ignoring it."
        )
    except subprocess.TimeoutExpired:
        pass
    finally:
        p.terminate()

        with lock:
            PROCS.pop(name, None)

        return (p.returncode, decode_bytes(stdout), decode_bytes(stderr))


def stop_proxy(
    name: str = "lueur", unset_http_proxy_variables: bool = False
) -> None:
    """
    Terminate a proxy by its name
    """
    with lock:
        p = PROCS.pop(name, None)
        if p is not None:
            p.terminate()

    if unset_http_proxy_variables:
        os.unsetenv("HTTP_PROXY")
        os.unsetenv("HTTPS_PROXY")


def with_normal_latency(
    mean: float = 100,
    stddev: float = 0,
    upstreams: str | list[str] = "*",
    side: Literal["client", "server"] = "server",
    direction: Literal["ingress", "egress"] = "ingress",
    per_read_write_op: bool = False,
    proxy_address: str = "0.0.0.0:8080",
    duration: float = 60,
    name: str = "lueur",
    set_http_proxy_variable: bool = False,
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> Tuple[int, str, str]:
    args = [
        "--proxy-address",
        proxy_address,
        "--with-latency",
        "--latency-distribution",
        "normal",
        "--latency-side",
        side,
        "--latency-direction",
        direction,
        "--latency-mean",
        str(mean),
        "--latency-stddev",
        str(stddev),
    ]

    if isinstance(upstreams, str):
        args.extend(["--upstream", upstreams])
    else:
        for u in upstreams:
            args.extend(["--upstream", u])

    if per_read_write_op:
        args.append("--latency-per-read-write")

    return run_proxy(name, args, duration)


def with_uniform_latency(
    min: float = 50,
    max: float = 150,
    upstreams: str | list[str] = "*",
    side: Literal["client", "server"] = "server",
    direction: Literal["ingress", "egress"] = "ingress",
    per_read_write_op: bool = False,
    proxy_address: str = "0.0.0.0:8080",
    duration: float = 60,
    name: str = "lueur",
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> Tuple[int, str, str]:
    args = [
        "--proxy-address",
        proxy_address,
        "--with-latency",
        "--latency-distribution",
        "uniform",
        "--latency-side",
        side,
        "--latency-direction",
        direction,
        "--latency-min",
        str(min),
        "--latency-max",
        str(max),
    ]

    if isinstance(upstreams, str):
        args.extend(["--upstream", upstreams])
    else:
        for u in upstreams:
            args.extend(["--upstream", u])

    if per_read_write_op:
        args.append("--latency-per-read-write")

    return run_proxy(name, args, duration)


def with_pareto_latency(
    shape: float = 50,
    scale: float = 10,
    upstreams: str | list[str] = "*",
    side: Literal["client", "server"] = "server",
    direction: Literal["ingress", "egress"] = "ingress",
    per_read_write_op: bool = False,
    proxy_address: str = "0.0.0.0:8080",
    duration: float = 60,
    name: str = "lueur",
    configuration: Configuration = None,
    secrets: Secrets = None,
) -> Tuple[int, str, str]:
    args = [
        "--proxy-address",
        proxy_address,
        "--with-latency",
        "--latency-distribution",
        "pareto",
        "--latency-side",
        side,
        "--latency-direction",
        direction,
        "--latency-shape",
        str(shape),
        "--latency-scale",
        str(scale),
    ]

    if isinstance(upstreams, str):
        args.extend(["--upstream", upstreams])
    else:
        for u in upstreams:
            args.extend(["--upstream", u])

    if per_read_write_op:
        args.append("--latency-per-read-write")

    return run_proxy(name, args, duration)
