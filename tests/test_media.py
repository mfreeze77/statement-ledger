import subprocess,shutil,wave,struct,math
from pathlib import Path
import pytest
from statement_ledger.media import clip_plan,local_clip
from statement_ledger.models import RightsGrant
from statement_ledger.transcripts import timestamp_ms,parse_timed_text,from_asr_export
from statement_ledger.speech import align_speaker_candidates,transcribe_local,diarize_local

@pytest.mark.parametrize("value,want",[("00:01:02.345",62345),("01:02,345",62345),("00:00:00.001",1)])
def test_timestamp(value,want):assert timestamp_ms(value)==want

def test_vtt_labels_are_not_people():
    t=parse_timed_text('WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<v Dana>Hello &amp; welcome</v>\n',"a","t")
    assert t.segments[0].text=="Hello & welcome"
    assert t.segments[0].speaker_label.startswith("vtt_")

def test_srt():
    t=parse_timed_text('1\n00:00:01,000 --> 00:00:02,000\nHello\n\n2\n00:00:03,000 --> 00:00:04,000\nWorld\n',"a","t")
    assert len(t.segments)==2 and t.segments[0].speaker_label=="unassigned"

def test_asr_export_keeps_unknown_speaker():
    t=from_asr_export({"segments":[{"start":1.234,"end":2.3,"text":" Hello "}]},"a","t",engine="import")
    assert t.segments[0].start_ms==1234 and t.segments[0].speaker_label=="unassigned"

def test_multi_speaker_segment_not_assigned_wholesale():
    result=align_speaker_candidates([{"start":0,"end":10,"text":"one sentence"}],
      [{"start_ms":0,"end_ms":9000,"speaker_label":"a"},{"start_ms":9000,"end_ms":10000,"speaker_label":"b"}])
    assert result[0]["speaker"]=="unassigned"

def test_single_speaker_candidate():
    r=align_speaker_candidates([{"start":0,"end":10,"text":"x"}],[{"start_ms":0,"end_ms":10000,"speaker_label":"a"}])
    assert r[0]["speaker"]=="a" and r[0]["attribution_status"]=="local_label_only"

@pytest.mark.parametrize("args",[(-1,10,100,0),(10,10,100,0),(0,101,100,0),(0,10,100,-1),(0.1,10,100,0)])
def test_invalid_clip_intervals(args):
    with pytest.raises(ValueError):clip_plan(*args)

def grant():return RightsGrant(id="r",source_id="manual_import",basis="Synthetic generated tone",allowed=["store_media","derive_clip","process_audio","store_text"],reviewed_by="test")

def test_clip_root_required(tmp_path):
    root=tmp_path/"root";root.mkdir();inp=tmp_path/"outside.wav";inp.write_bytes(b'x')
    with pytest.raises(ValueError):local_clip(inp,root/"out.m4a",clip_plan(0,1000,2000),grant(),root)

@pytest.mark.skipif(shutil.which("ffmpeg") is None,reason="FFmpeg not installed")
def test_real_ffmpeg_clipping_generated_audio(tmp_path):
    inp=tmp_path/"tone.wav"
    with wave.open(str(inp),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000)
        w.writeframes(b''.join(struct.pack('<h',int(5000*math.sin(2*math.pi*440*i/16000))) for i in range(32000)))
    out=tmp_path/"clip.m4a"
    local_clip(inp,out,clip_plan(500,1500,2000,0),grant(),tmp_path)
    assert out.stat().st_size>0 and inp.exists()
    duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(out)]))
    assert abs(duration-1)<.15

def test_optional_transcriber_with_fake_model(tmp_path):
    from types import SimpleNamespace as NS
    path=tmp_path/"a.wav";path.write_bytes(b'not-real')
    class Fake:
        def __init__(self,*args,**kw):pass
        def transcribe(self,*args,**kw):return [NS(start=0,end=1,text="Synthetic",words=[])],NS(language="en")
    out=transcribe_local(path,grant(),model_factory=Fake)
    assert out["segments"][0]["speaker"]=="unassigned"
