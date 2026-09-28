"""Import timed text or an existing ASR export. No identity is inferred from labels."""
from __future__ import annotations
import re, html
from decimal import Decimal, ROUND_HALF_UP
from .models import Segment, Transcript


def seconds_ms(value) -> int:
    d=Decimal(str(value))
    if not d.is_finite() or d<0:raise ValueError("Invalid timestamp")
    return int((d*1000).quantize(Decimal("1"),rounding=ROUND_HALF_UP))

def timestamp_ms(value: str) -> int:
    value=value.replace(",",".")
    parts=value.split(":")
    if len(parts)==2:h,m,s="0",*parts
    elif len(parts)==3:h,m,s=parts
    else:raise ValueError("Timestamp must be HH:MM:SS.mmm or MM:SS.mmm")
    if not h.isdigit() or not m.isdigit() or int(m)>=60 or Decimal(s)>=60:raise ValueError("Invalid timestamp")
    return seconds_ms(Decimal(h)*3600+Decimal(m)*60+Decimal(s))

def parse_timed_text(text: str, asset_id: str, transcript_id: str, *, engine: str="timed-text-import") -> Transcript:
    segments=[]
    lines=text.replace("\r\n","\n").replace("\r","\n").split("\n")
    i=0
    while i<len(lines):
        if "-->" not in lines[i]:i+=1;continue
        left,right=lines[i].split("-->",1)
        start,end=timestamp_ms(left.strip()),timestamp_ms(right.strip().split()[0])
        i+=1;body=[]
        while i<len(lines) and lines[i].strip():body.append(lines[i]);i+=1
        raw="\n".join(body)
        match=re.search(r"<v(?:\.[^ >]+)?\s+([^>]+)>",raw)
        # Voice names in VTT are labels, not confirmed real-world identities.
        label=("vtt_"+__import__('hashlib').sha256(match.group(1).encode()).hexdigest()[:12]) if match else "unassigned"
        cleaned=html.unescape(re.sub(r"<[^>]*>","",raw)).strip()
        if cleaned:segments.append(Segment(start_ms=start,end_ms=end,speaker_label=label,text=cleaned))
    if not segments:raise ValueError("No timed cues found")
    return Transcript(id=transcript_id,asset_id=asset_id,engine=engine,segments=segments)

def from_asr_export(data: dict, asset_id: str, transcript_id: str, *, engine: str) -> Transcript:
    # Compatible with standard segment-shaped faster-whisper/WhisperX JSON exports.
    # Word-level quality/precision is NOT invented; original export should be retained.
    segments=[]
    for row in data.get("segments",[]):
        label=str(row.get("speaker") or "unassigned")
        segments.append(Segment(start_ms=seconds_ms(row["start"]),end_ms=seconds_ms(row["end"]),
            speaker_label=label,text=row["text"].strip(),overlap=bool(row.get("overlap",False))))
    return Transcript(id=transcript_id,asset_id=asset_id,engine=engine,
                      language=data.get("language","und"),segments=segments,precision="segment")
