"""Execute a reviewed localization plan on authorized local media.

Exports timebase-aware candidates. Does not create confirmed identity mappings.
Interrupted runs leave a manifest describing completed clips; no hidden resume.
"""
from pathlib import Path
import hashlib,json,subprocess
from .profiles import current
from .models import RightsGrant
from .policy import require_right
from .media import clip_plan,local_clip
from .speech import transcribe_local,diarize_local,align_speaker_candidates
from .util import digest


def _hash(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        while chunk:=f.read(1024*1024):h.update(chunk)
    return h.hexdigest()

def process_localization(ledger,run_id,input_path,output_dir,media_root,*,transcribe=False,diarize=False,
                         model="small",hf_token=None,clipper=local_clip,transcriber=transcribe_local,diarizer=diarize_local):
    r=current(ledger,"localization_run",run_id)
    asset=current(ledger,"asset",r["payload"]["asset_id"])
    grant=RightsGrant.model_validate(current(ledger,"rights",asset["payload"]["rights_id"])["payload"])
    for right in ("store_media","derive_clip","process_audio"):require_right(grant,right)
    if transcribe:require_right(grant,"store_text")
    source=Path(input_path).resolve();root=Path(media_root).resolve();out=Path(output_dir).resolve()
    if not source.is_relative_to(root) or not out.is_relative_to(root):raise ValueError("Media paths must stay within media_root")
    if not source.is_file() or not asset["payload"]["content_sha256"] or _hash(source)!=asset["payload"]["content_sha256"]:
        raise ValueError("Local media does not match the registered asset content hash")
    if out.exists():raise ValueError("Output directory already exists; inspect its manifest before choosing a new run")
    # Check runtime before creating partial output. Fakes used by unit tests bypass probe.
    out.mkdir(parents=True)
    manifest={"format":"localization-media-v1","run_id":run_id,"run_revision":r["revision"],
        "source_asset_id":asset["id"],"source_sha256":asset["payload"]["content_sha256"],
        "items":[],"status":"running","identities_confirmed":False,"publication_authorized":False}
    def save():
        temp=out/"manifest.tmp";temp.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8");temp.replace(out/"manifest.json")
    save()
    try:
        for i,window in enumerate(r["payload"]["selected_intervals"]):
            # Recheck expiry/revision before every expensive task, not only once at startup.
            current(ledger,"localization_run",run_id)
            prefix=f"window-{i:04d}";path=out/f"{prefix}.m4a"
            plan=clip_plan(window["start_ms"],window["end_ms"],r["payload"]["duration_ms"],0)
            clipper(source,path,plan,grant,root)
            item={"index":i,"path":path.name,"source_start_ms":window["start_ms"],"source_end_ms":window["end_ms"],
                "content_sha256":_hash(path),"timebase":"clip_relative_plus_source_start_ms","identity_confirmed":False}
            if clipper is local_clip:
                probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(path)],capture_output=True,text=True,check=True,timeout=30)
                measured=float(json.loads(probe.stdout)["format"]["duration"])*1000
                item["probed_duration_ms"]=measured
                if abs(measured-(window["end_ms"]-window["start_ms"]))>250:
                    raise ValueError("Derived clip duration differs from request; review timeline before proceeding")
            output=transcriber(path,grant,model=model) if transcribe else {}
            if diarize:
                diar=diarizer(path,grant,token=hf_token);output["diarization"]=diar
                if transcribe:output["segments"]=align_speaker_candidates(output["segments"],diar["turns"])
            # Preserve clip-relative coordinates; supply source positions separately.
            offset=window["start_ms"]
            for s in output.get("segments",[]):
                s["source_start_ms"]=offset+round(s["start"]*1000);s["source_end_ms"]=offset+round(s["end"]*1000)
                label=s.get("speaker","unassigned")
                s["speaker"]=f"{prefix}:{label}" if label not in {"unassigned","unknown"} else "unassigned"
            for turn in output.get("diarization",{}).get("turns",[]):
                turn["source_start_ms"]=offset+turn["start_ms"];turn["source_end_ms"]=offset+turn["end_ms"]
                turn["speaker_label"]=f'{prefix}:{turn["speaker_label"]}'
            item["processing"]=output;manifest["items"].append(item);save()
        manifest["status"]="completed";save()
    except Exception as exc:
        manifest["status"]="failed";manifest["error_type"]=type(exc).__name__;save();raise
    return manifest
