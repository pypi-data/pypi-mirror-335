from __future__ import annotations

import atexit
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from uv import find_uv_bin

IS_WINDOWS = sys.platform.startswith("win")


def run(script: str, args: list[str], lockfile_contents: str | None, dir: Path) -> None:  # noqa: A002
    with tempfile.NamedTemporaryFile(
        mode="w+",
        delete=False,
        suffix=".py",
        dir=dir,
        prefix="juv.tmp.",
        encoding="utf-8",
    ) as f:
        script_path = Path(f.name)
        lockfile = Path(f"{f.name}.lock")
        f.write(script)
        f.flush()

        env = os.environ.copy()

        if lockfile_contents:
            # Write the contents so UV picks it up
            lockfile.write_text(lockfile_contents)
            # Forward path to underlying process.
            # We rewrite the lockfile entry (if necessary) within that process.
            env["JUV_LOCKFILE_PATH"] = str(lockfile)

        if not IS_WINDOWS:
            process = subprocess.Popen(  # noqa: S603
                [os.fsdecode(find_uv_bin()), *args, f.name],
                stdout=sys.stdout,
                stderr=sys.stderr,
                preexec_fn=os.setsid,  # noqa: PLW1509
                env=env,
            )
        else:
            process = subprocess.Popen(  # noqa: S603
                [os.fsdecode(find_uv_bin()), *args, f.name],
                stdout=sys.stdout,
                stderr=sys.stderr,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                env=env,
            )

        try:
            process.wait()
        except KeyboardInterrupt:
            if not IS_WINDOWS:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                os.kill(process.pid, signal.SIGTERM)
        finally:
            lockfile.unlink(missing_ok=True)

        # ensure the process is fully cleaned up before deleting script
        process.wait()
        atexit.register(lambda: script_path.unlink(missing_ok=True))
