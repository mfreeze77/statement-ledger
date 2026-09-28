"""Timeline planning and local clipping. No remote downloader or identity guessing."""

import subprocess
from pathlib import Path

from statement_ledger.contracts.models import RightsGrant
from statement_ledger.core.policy import require_right


def clip_plan(start_ms: int, end_ms: int, duration_ms: int, padding_ms: int = 15000) -> dict:
    if any(type(v) is not int for v in (start_ms, end_ms, duration_ms, padding_ms)):
        raise ValueError("Clip coordinates must be integer milliseconds")
    if start_ms < 0 or end_ms <= start_ms or end_ms > duration_ms or padding_ms < 0:
        raise ValueError("Invalid clip interval")
    return {
        "speech_start_ms": start_ms,
        "speech_end_ms": end_ms,
        "context_start_ms": max(0, start_ms - padding_ms),
        "context_end_ms": min(duration_ms, end_ms + padding_ms),
        "source_duration_ms": duration_ms,
        "precision": "requested; output must be probed before being treated as exact",
    }


def local_clip(
    input_path: Path, output_path: Path, plan: dict, grant: RightsGrant, media_root: Path
) -> None:
    require_right(grant, "store_media")
    require_right(grant, "derive_clip")
    root = media_root.resolve()
    source = input_path.resolve()
    destination = output_path.resolve()
    if not source.is_relative_to(root) or not destination.is_relative_to(root):
        raise ValueError("Both media paths must be inside media_root")
    if not source.is_file() or destination.exists():
        raise ValueError("Input must exist and output must not already exist")
    if source == destination:
        raise ValueError("Never overwrite source media")
    duration = (plan["context_end_ms"] - plan["context_start_ms"]) / 1000
    if duration <= 0:
        raise ValueError("Empty clip")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Re-encode rather than falsely claim keyframe-only stream copy is exact.
    command = [
        "ffmpeg",
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-protocol_whitelist",
        "file,pipe",
        "-i",
        str(source),
        "-ss",
        f"{plan['context_start_ms'] / 1000:.3f}",
        "-t",
        f"{duration:.3f}",
    ]
    if destination.suffix.lower() in {".m4a", ".wav"}:
        command += [
            "-vn",
            "-map",
            "0:a:0",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le" if destination.suffix.lower() == ".wav" else "aac",
        ]
    else:
        command += ["-map", "0:v?", "-map", "0:a?", "-c:v", "libx264", "-c:a", "aac"]
    command += ["-n", str(destination)]
    try:
        subprocess.run(command, check=True, timeout=600, capture_output=True)
    except (subprocess.SubprocessError, FileNotFoundError) as exc:
        destination.unlink(missing_ok=True)
        raise RuntimeError("Local clipping failed; verify FFmpeg and authorized media") from exc
