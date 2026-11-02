"""Speech-to-text with faster-whisper (runs locally on CPU)."""
from dataclasses import dataclass

from faster_whisper import WhisperModel

LOW_CONFIDENCE = -1.0  # avg_logprob below this gets flagged for the journalist


@dataclass
class Segment:
    start: float
    end: float
    text: str
    low_confidence: bool


def load_model(size: str = "small") -> WhisperModel:
    # int8 keeps memory low so it runs on ordinary laptops
    return WhisperModel(size, device="cpu", compute_type="int8")


def mmss(seconds: float) -> str:
    return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"


def transcribe(model: WhisperModel, path: str, language: str | None = None):
    """Returns (segments, detected_language). language=None means auto-detect."""
    segs, info = model.transcribe(path, language=language, vad_filter=True)
    out = [
        Segment(s.start, s.end, s.text.strip(), s.avg_logprob < LOW_CONFIDENCE)
        for s in segs
    ]
    return out, info.language


def to_text(segments: list[Segment]) -> str:
    """Editable transcript. '??' marks passages the model was unsure about."""
    lines = []
    for s in segments:
        flag = " ??" if s.low_confidence else ""
        lines.append(f"[{mmss(s.start)}] {s.text}{flag}")
    return "\n".join(lines)
