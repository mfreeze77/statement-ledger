"""Optional local inference adapters. Neither assigns real person names.

Core installation does not install GPU/ML dependencies or download weights.
Run only on authorized local assets. Import-level code is tested with fakes;
actual model inference is an integration gate requiring weights and hardware.
"""

from pathlib import Path

from statement_ledger.contracts.models import RightsGrant
from statement_ledger.core.policy import require_right
from statement_ledger.core.time import seconds_ms


def transcribe_local(
    path: Path,
    grant: RightsGrant,
    *,
    model: str = "small",
    device: str = "cpu",
    compute_type: str = "int8",
    model_factory=None,
) -> dict:
    require_right(grant, "process_audio")
    require_right(grant, "store_text")
    if not path.is_file():
        raise ValueError("Audio input must be a local file")
    if model_factory is None:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise RuntimeError(
                "Install optional faster-whisper in a separate worker environment"
            ) from None
        model_factory = WhisperModel
    instance = model_factory(model, device=device, compute_type=compute_type)
    segments, info = instance.transcribe(str(path), vad_filter=True, word_timestamps=True)
    return {
        "engine": "faster-whisper",
        "model": model,
        "language": info.language,
        "segments": [
            {
                "start": s.start,
                "end": s.end,
                "text": s.text,
                "speaker": "unassigned",
                "words": [
                    {"start": w.start, "end": w.end, "word": w.word, "probability": w.probability}
                    for w in (s.words or [])
                ],
            }
            for s in segments
        ],
    }


def diarize_local(
    path: Path, grant: RightsGrant, *, token: str | None = None, pipeline_factory=None
) -> dict:
    require_right(grant, "process_audio")
    if not path.is_file():
        raise ValueError("Audio input must be a local file")
    if pipeline_factory is None:
        try:
            from pyannote.audio import Pipeline
        except ImportError:
            raise RuntimeError(
                "Install optional pyannote.audio and accept model terms in worker environment"
            ) from None
        pipeline_factory = Pipeline.from_pretrained
    pipeline = pipeline_factory("pyannote/speaker-diarization-community-1", token=token)
    output = pipeline(str(path))
    annotation = output.speaker_diarization if hasattr(output, "speaker_diarization") else output
    turns = [
        {
            "start_ms": seconds_ms(turn.start),
            "end_ms": seconds_ms(turn.end),
            "speaker_label": speaker,
        }
        for turn, _, speaker in annotation.itertracks(yield_label=True)
    ]
    return {
        "engine": "pyannote",
        "model": "speaker-diarization-community-1",
        "turns": turns,
        "identities_confirmed": False,
    }


def align_speaker_candidates(
    segments: list[dict], turns: list[dict], *, threshold: float = 0.8
) -> list[dict]:
    """Conservative segment overlap match; crossing/overlapping turns remain unassigned.

    Not forced alignment. An ASR segment covering two speakers must be subdivided or
    reviewed; never assign it wholesale merely to whichever speaker spoke longest.
    """
    if not 0.5 <= threshold <= 1:
        raise ValueError("threshold must be 0.5..1")
    out = []
    for seg in segments:
        start, end = seconds_ms(seg["start"]), seconds_ms(seg["end"])
        if end <= start:
            raise ValueError("ASR interval is empty")
        hits = {}
        for turn in turns:
            n = max(0, min(end, turn["end_ms"]) - max(start, turn["start_ms"]))
            if n:
                hits[turn["speaker_label"]] = hits.get(turn["speaker_label"], 0) + n
        # Multiple labels are explicitly unresolved, even if one dominates.
        certain = len(hits) == 1 and next(iter(hits.values())) / (end - start) >= threshold
        relevant = [t for t in turns if min(end, t["end_ms"]) > max(start, t["start_ms"])]
        actual_overlap = any(
            a["speaker_label"] != b["speaker_label"]
            and min(end, a["end_ms"], b["end_ms"]) > max(start, a["start_ms"], b["start_ms"])
            for i, a in enumerate(relevant)
            for b in relevant[i + 1 :]
        )
        out.append(
            {
                **seg,
                "speaker": next(iter(hits)) if certain else "unassigned",
                "overlap": actual_overlap,
                "speaker_boundary_uncertain": len(hits) > 1,
                "speaker_candidates": list(hits),
                "attribution_status": "local_label_only" if certain else "unresolved",
            }
        )
    return out


def verify_speaker_clips(
    reference: Path,
    candidate: Path,
    reference_grant: RightsGrant,
    candidate_grant: RightsGrant,
    *,
    model_directory: Path,
    model_revision: str,
    model_factory=None,
) -> dict:
    """Optional local ECAPA comparison. Inputs must be operator-selected isolated clips.

    No model download is performed by this function. Use a pre-provisioned, pinned local
    model directory and review its license. A cosine similarity is NOT a probability.
    This function does not enroll a person or modify a SpeakerMapping.
    """
    import hashlib
    import math

    for grant in (reference_grant, candidate_grant):
        require_right(grant, "process_audio")
        require_right(grant, "process_biometrics")
    for path in (reference, candidate):
        if not path.is_file():
            raise ValueError("Speaker verification needs local clip files")
    if not model_directory.is_dir() or not model_revision.strip():
        raise ValueError("A pinned, pre-provisioned local model directory is required")
    if model_factory is None:
        try:
            from speechbrain.inference.speaker import SpeakerRecognition
        except ImportError:
            raise RuntimeError(
                "Install optional speechbrain in the isolated audio worker"
            ) from None
        model_factory = SpeakerRecognition.from_hparams
    model = model_factory(
        source=str(model_directory), savedir=str(model_directory), run_opts={"device": "cpu"}
    )
    score, prediction = model.verify_files(str(reference), str(candidate))
    score = float(score.item()) if hasattr(score, "item") else float(score)
    if not math.isfinite(score) or not -1 <= score <= 1:
        raise ValueError("Invalid cosine similarity")

    def sha(path):
        h = hashlib.sha256()
        with path.open("rb") as f:
            while block := f.read(1024 * 1024):
                h.update(block)
        return h.hexdigest()

    return {
        "engine": "speechbrain-ecapa",
        "model_revision": model_revision,
        "reference_sha256": sha(reference),
        "candidate_sha256": sha(candidate),
        "cosine_similarity": score,
        "identity_confirmed": False,
        "probability": None,
        "limitation": "Advisory comparison of operator-selected clips; overlap, replay and impersonation remain review concerns.",
    }
