"""Loss-preserving source parsers. Outputs are observations, never accepted statements.

Huge corpora use line-delimited gzip/bzip2 streams. Root-array JSON is deliberately
bounded (64 MiB decompressed by default); convert larger arrays to JSONL externally.
Malformed rows are not silently skipped. The caller can quarantine and resume.
"""
from __future__ import annotations
import bz2, gzip, json
from pathlib import Path
from typing import Iterator, Any
from .registry import source
from ..models import Observation
from ..util import digest, stable_id

PARSER_VERSION = "1.0.0"
MAX_LINE = 8 * 1024 * 1024

class ParseError(ValueError):
    pass

def open_text(path: Path):
    if path.suffix == ".gz": return gzip.open(path, "rt", encoding="utf-8-sig")
    if path.suffix == ".bz2": return bz2.open(path, "rt", encoding="utf-8-sig")
    return path.open("rt", encoding="utf-8-sig")

def iter_rows(path: Path, *, max_records: int = 100_000, max_line: int = MAX_LINE,
              max_json_bytes: int = 64 * 1024 * 1024) -> Iterator[dict]:
    if max_records < 1 or max_line < 1 or max_json_bytes < 1:
        raise ValueError("Input bounds must be positive")
    with open_text(path) as f:
        first = f.read(1)
        while first and first.isspace(): first = f.read(1)
        if not first: return
        if first == "[":
            # Explicit bounded array import; never json.load an unbounded corpus.
            tail = f.read(max_json_bytes + 1)
            if len(tail.encode("utf-8")) > max_json_bytes:
                raise ParseError("JSON array exceeds configured bound; convert to JSONL")
            try: data = json.loads("[" + tail)
            except json.JSONDecodeError as e: raise ParseError("Invalid JSON array") from e
            if not isinstance(data, list): raise ParseError("Expected array")
            for row in data[:max_records]:
                if not isinstance(row, dict): raise ParseError("Every row must be an object")
                yield row
            return
        # JSONL supports objects only; pretty-printed single objects use .json mode
        # via read_document instead. This prevents unbounded buffering ambiguity.
        prefix = first
        for number in range(1, max_records + 1):
            line = prefix + f.readline(max_line + 1)
            prefix = ""
            if not line: return
            if len(line.encode("utf-8")) > max_line: raise ParseError(f"Line {number} exceeds limit")
            if not line.strip(): continue
            try: row = json.loads(line)
            except json.JSONDecodeError as e: raise ParseError(f"Invalid JSONL at physical line {number}") from e
            if not isinstance(row, dict): raise ParseError(f"Line {number} is not an object")
            yield row

def read_document(path: Path, max_bytes: int = 64 * 1024 * 1024) -> Any:
    with open_text(path) as f: value = f.read(max_bytes + 1)
    if len(value.encode("utf-8")) > max_bytes: raise ParseError("Document exceeds bound")
    return json.loads(value)

def _obs(sid: str, rid: str, rights: str, kind: str, url: str, raw: dict,
         *, title: str = "", text: str | None = None, speaker: str | None = None,
         published: str | None = None, links: list[str] | None = None) -> Observation:
    return Observation(id=stable_id(sid, rid), source_id=sid, native_id=rid, rights_id=rights,
        kind=kind, url=url, title=title, text=text, reported_speaker=speaker,
        published_at=published, links=list(dict.fromkeys(links or [])), raw_payload=raw,
        raw_sha256=digest(raw), parser_version=PARSER_VERSION)

def _urls(value) -> list[str]:
    if value is None: return []
    if isinstance(value, str): return [value]
    if isinstance(value, list):
        out=[]
        for v in value:
            if isinstance(v, str): out.append(v)
            elif isinstance(v, dict) and isinstance(v.get("url"), str): out.append(v["url"])
        return out
    if isinstance(value, dict) and isinstance(value.get("url"), str): return [value["url"]]
    return []

def parse(sid: str, row: dict, rights: str) -> list[Observation]:
    adapter = source(sid)["parser"]
    if adapter is None: raise ParseError(f"No parser for {sid}; use an authorized manual envelope")
    try:
        if adapter == "quotebank":
            urls = _urls(row.get("urls") or row.get("url"))
            if not urls: raise ParseError("Quotation lacks source URL")
            quote = row.get("quotation")
            if not isinstance(quote, str) or not quote: raise ParseError("Missing quotation")
            return [_obs(sid,str(row.get("quoteID") or digest(row)),rights,"quotation_lead",urls[0],row,
                text=quote,speaker=row.get("speaker"),published=None,links=urls)]
        if adapter == "gdelt_gqg":
            out=[]
            for i,q in enumerate(row.get("quotes",[])):
                if not isinstance(q,dict) or not isinstance(q.get("quote"),str): raise ParseError("Invalid nested quotation")
                raw={"article":{k:v for k,v in row.items() if k!="quotes"},"quote_index":i,"quotation":q}
                out.append(_obs(sid,f'{row["url"]}|{row.get("date", "")}|{i}',rights,"quotation_lead",row["url"],raw,
                    title=row.get("title", ""),text=q["quote"],published=None))
            return out
        if adapter == "youtube":
            out=[]
            for item in row.get("items", [row] if "snippet" in row else []):
                snippet=item.get("snippet",{}); ident=item.get("id")
                vid=ident.get("videoId") if isinstance(ident,dict) else ident
                vid=snippet.get("resourceId",{}).get("videoId", vid)
                if not vid: continue # Search may include non-video results.
                if isinstance(ident,dict) and ident.get("kind") not in (None,"youtube#video"): continue
                out.append(_obs(sid,str(vid),rights,"appearance_lead",f"https://www.youtube.com/watch?v={vid}",item,
                    title=snippet.get("title", ""),text=snippet.get("description") or None,
                    published=snippet.get("publishedAt")))
            return out
        if adapter == "google_fact_check":
            out=[]
            for claim in row.get("claims", [row] if "claimReview" in row else []):
                for review in claim.get("claimReview",[]):
                    url=review["url"]
                    # Different claims reviewed at the same article URL remain separate.
                    rid=f'{url}|{digest({"text":claim.get("text"),"date":claim.get("claimDate"),"claimant":claim.get("claimant")})}'
                    raw={"claim":{k:v for k,v in claim.items() if k!="claimReview"},"review":review}
                    out.append(_obs(sid,rid,rights,"external_review",url,raw,title=review.get("title", ""),
                        text=claim.get("text"),speaker=claim.get("claimant"),published=review.get("reviewDate")))
            return out
        if adapter in {"claimreview","fact_check_insights"}:
            nodes=row.get("@graph",[row]); out=[]
            for node in nodes:
                typ=node.get("@type", "ClaimReview" if adapter=="fact_check_insights" else "")
                if "ClaimReview" not in (typ if isinstance(typ,list) else [typ]): continue
                url=node.get("url") or node.get("@id")
                if not url: raise ParseError("ClaimReview requires a source URL")
                item=node.get("itemReviewed") or {}; author=item.get("author") or {}
                author_name=author.get("name") if isinstance(author,dict) else None
                links=_urls(item.get("appearance"))+_urls(item.get("firstAppearance"))
                out.append(_obs(sid,str(node.get("id") or f'{url}|{digest(node.get("claimReviewed"))}'),rights,"external_review",url,node,
                    title=node.get("name", ""),text=node.get("claimReviewed"),speaker=author_name,
                    published=node.get("datePublished"),links=links))
            return out
        if adapter == "internet_archive":
            docs=row.get("response",{}).get("docs")
            docs=docs if docs is not None else [row.get("metadata",row)]
            out=[]
            for item in docs:
                ident=item["identifier"];title=item.get("title","")
                if isinstance(title,list):title="; ".join(str(x) for x in title)
                out.append(_obs(sid,str(ident),rights,"metadata",f"https://archive.org/details/{ident}",item,
                    title=str(title),published=None))
            return out
        if adapter == "aapb":
            if "response" not in row and "docs" not in row: raise ParseError("Unrecognized AAPB metadata shape")
            docs=row.get("response",{}).get("docs",row.get("docs",[])); out=[]
            for item in docs:
                ident=item["id"];title=item.get("title","")
                if isinstance(title,list):title="; ".join(str(x) for x in title)
                out.append(_obs(sid,str(ident),rights,"metadata",f"https://americanarchive.org/catalog/{ident}",item,title=str(title)))
            if not out and docs==[]: return []
            return out
        if adapter == "manual":
            # Supplied source_id may name a contract-only source; operator owns rights review.
            actual=row.get("source_id",sid);source(actual)
            return [_obs(actual,str(row["native_id"]),rights,row["kind"],row["url"],row,
                title=row.get("title", ""),text=row.get("text"),speaker=row.get("reported_speaker"),
                published=row.get("published_at"),links=row.get("links",[]))]
    except (KeyError,TypeError,AttributeError) as e:
        raise ParseError(f"Unexpected {sid} source shape; retain raw record and quarantine") from e
    raise ParseError(f"Unsupported adapter: {adapter}")
