"use strict";
let token="";
const content=document.getElementById("content"),status=document.getElementById("status");
function el(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;}
function reset(title){content.replaceChildren(el("h2",title));}
function raw(data){const p=el("pre",JSON.stringify(data,null,2));content.append(p);}
async function api(path,options={}){const r=await fetch(path,{...options,headers:{Authorization:`Bearer ${token}`,"Content-Type":"application/json",...(options.headers||{})}});const data=await r.json();if(!r.ok)throw new Error(data.detail||`HTTP ${r.status}`);return data;}
function safeLink(url,text){const a=el("a",text);try{const u=new URL(url);if(!["http:","https:"].includes(u.protocol))return a;a.href=u.href;a.target="_blank";a.rel="noopener noreferrer";}catch{}return a;}
async function people(){reset("People and appearance records");const data=await api("/api/records/person");const wrap=el("div",undefined,"cards");for(const row of data.items){const c=el("div",undefined,"card");c.append(el("h3",row.payload.display_name));if(row.payload.synthetic)c.append(el("span","SYNTHETIC FIXTURE","badge"));c.append(el("p",`Revision ${row.revision} · ${row.stale?"Needs revalidation":"Current"}`,"muted"));const b=el("button","Open statement ledger");b.onclick=()=>guard(()=>person(row.id));c.append(b);wrap.append(c);}content.append(wrap);if(!data.items.length)content.append(el("p","No people yet. Seed a subject through the CLI or create a person through the API."));}
async function person(id){const data=await api(`/api/people/${encodeURIComponent(id)}/ledger`);reset(data.person.payload.display_name);content.append(el("p",data.coverage_statement,"muted"));const metrics=el("div",undefined,"metrics");for(const [k,v] of Object.entries(data.counts)){const box=el("div",undefined,"metric");box.append(el("strong",String(v)),el("span",k.replaceAll("_"," ")));metrics.append(box);}content.append(metrics,el("p",data.deduplication_limit,"muted"));for(const item of data.items){const c=el("article",undefined,"card");c.append(el("span",`${item.asset_role} · event ${item.event_id}`,"badge"),el("blockquote",item.exact_text));c.append(el("p",`Source ${item.source_start_ms/1000}–${item.source_end_ms/1000}s · event ${item.event_start_ms/1000}–${item.event_end_ms/1000}s`,"muted"));c.append(safeLink(item.source_url,"Open preserved source reference"));for(const review of item.reviews){c.append(el("h4",`Recorded review: ${review.payload.finding}`),el("p",review.payload.rationale));}const detail=el("details");detail.append(el("summary","Provenance and record IDs"),el("pre",JSON.stringify(item,null,2)));c.append(detail);content.append(c);}if(data.exclusions.length){content.append(el("h3","Excluded from aligned counts"));raw(data.exclusions);}content.append(el("h3","Coverage records"));raw(data.coverage);}
async function sources(){reset("Source connector registry");const data=await api("/api/sources");const wrap=el("div",undefined,"cards");for(const s of data.sources){const c=el("div",undefined,"card");c.append(el("h3",s.name),el("span",s.implementation,"badge"),el("p",s.limitations),el("p",s.next_step,"muted"));c.append(safeLink(s.documentation_urls[0],"Source documentation"));wrap.append(c);}content.append(wrap);}
async function plan(){reset("Plan a bounded investigation");const name=el("input");name.placeholder="Person name";const b=el("button","Generate plan — no network calls");b.onclick=()=>guard(async()=>{const result=await api("/api/discovery/plan",{method:"POST",body:JSON.stringify({name:name.value})});const old=content.querySelector("pre");if(old)old.remove();raw(result);});content.append(name,b);}
async function records(){reset("Raw record inspector");const kind=el("select");for(const k of ["person","rights","observation","event","appearance","asset","transcript","speaker_mapping","utterance","proposition","occurrence","evidence","review","correction","coverage_run","speaker_profile","localization_run","decision_run","claim_family","claim_card"]){const opt=el("option",k);opt.value=k;kind.append(opt);}const b=el("button","Load first 100 records");b.onclick=()=>guard(async()=>{const old=content.querySelector("pre");if(old)old.remove();raw(await api(`/api/records/${kind.value}`));});content.append(kind,b);}
async function integrity(){reset("Integrity checks");raw(await api("/api/integrity"));content.append(el("p","Hash consistency is not an external timestamp or proof against a database administrator rewriting history.","muted"));}
async function guard(fn){try{await fn();status.textContent="Connected to private workspace.";status.className="";}catch(e){status.textContent=e.message;status.className="error";}}
document.getElementById("connect").onclick=()=>{token=document.getElementById("token").value;document.getElementById("token").value="";guard(people);};
for(const b of document.querySelectorAll("[data-view]")){b.onclick=()=>guard(({people,sources,plan,records,integrity,profiles,localization,claims})[b.dataset.view]);}

async function profiles(){
 reset("Learned phrase profiles");
 content.append(el("p","Profiles learn from accepted, reviewed turns. Frequency is measured by original event, not copied uploads. These are language features—not proof of identity.","muted"));
 const data=await api("/api/records/speaker_profile");
 for(const r of data.items){const card=el("article",undefined,"card");card.append(el("h3",r.payload.person_id),el("span",r.stale?"STALE — REBUILD REQUIRED":r.payload.readiness,"badge"));
 card.append(el("p",`${r.payload.target_event_ids.length} target events · ${r.payload.background_event_ids.length} comparison events · ${r.payload.features.length} features`));
 const table=el("table");const head=el("tr");for(const t of ["Category","Phrase","Target events","Other events"])head.append(el("th",t));table.append(head);
 for(const f of r.payload.features.slice(0,15)){const tr=el("tr");for(const v of [f.category,f.phrase,f.target_events,f.background_events])tr.append(el("td",String(v)));table.append(tr);}card.append(table);
 const details=el("details");details.append(el("summary","Profile provenance and full feature list"),el("pre",JSON.stringify(r,null,2)));card.append(details);content.append(card);}
 if(!data.items.length)content.append(el("p","No profile has been built. Run demo-acceleration in a separate empty database or build one from confirmed turns."));
}
async function localization(){
 reset("Transcript-first speaker windows");content.append(el("p","Shadow mode retains full audio. Assist mode proposes a smaller research workload. Neither mode confirms identity or proves that unprocessed regions lack the target.","muted"));
 const ps=await api("/api/records/speaker_profile"),ts=await api("/api/records/transcript");
 const p=el("select"),t=el("select"),mode=el("select");
 for(const r of ps.items){const o=el("option",`${r.id}${r.stale?" (stale)":""}`);o.value=r.id;p.append(o);}
 for(const r of ts.items){const o=el("option",r.id);o.value=r.id;t.append(o);}
 for(const name of ["shadow","assist"]){const o=el("option",name);o.value=name;mode.append(o);}
 p.setAttribute("aria-label","Speaker profile");t.setAttribute("aria-label","Transcript");mode.setAttribute("aria-label","Processing mode");
 const b=el("button","Build local plan — no Jev call");b.onclick=()=>guard(async()=>{const result=await api("/api/localization/plan",{method:"POST",body:JSON.stringify({profile_id:p.value,transcript_id:t.value,config:{mode:mode.value}})});renderWindowPlan(result.run);});
 content.append(p,t,mode,b,el("h3","Existing plans"));const data=await api("/api/records/localization_run");
 for(const r of data.items){const open=el("button",`${r.payload.config.mode} · ${r.id}${r.stale?" (stale)":""}`);open.onclick=()=>renderWindowPlan(r);content.append(open);}
}
function renderWindowPlan(r){
 const existing=content.querySelector(".window-result");if(existing)existing.remove();const box=el("article",undefined,"card window-result"),p=r.payload;
 box.append(el("h3",`${p.config.mode} plan · ${p.transcript_id}`),el("p",`${(p.selected_audio_ms/60000).toFixed(2)} / ${(p.duration_ms/60000).toFixed(2)} audio minutes selected · ${(p.audio_reduction_fraction*100).toFixed(1)}% fewer audio minutes in this plan`));
 box.append(el("p","Not a measured cost reduction or speaker-recall estimate. Identity remains unconfirmed.","muted"));
 for(const it of p.selected_intervals)box.append(el("p",`${(it.start_ms/1000).toFixed(1)}–${(it.end_ms/1000).toFixed(1)} seconds`));
 if(p.fallback_reasons.length)box.append(el("p",`Fallbacks: ${p.fallback_reasons.join(", ")}`));
 const d=el("details");d.append(el("summary","Windows, audits, gaps and provenance"),el("pre",JSON.stringify(r,null,2)));box.append(d);content.append(box);
}
async function claims(){
 reset("Shared claim and evidence library");content.append(el("p","A proposition can recur across many people and sources. Search finds candidates; scope and current evidence still need review. Families do not imply equivalence.","muted"));
 const input=el("input");input.placeholder="Search claim wording";input.setAttribute("aria-label","Claim search");const b=el("button","Search local claim index"),results=el("div");
 b.onclick=()=>guard(async()=>{results.replaceChildren();const data=await api("/api/claims/search",{method:"POST",body:JSON.stringify({text:input.value})});
 for(const item of data.items){const c=el("article",undefined,"card");c.append(el("h3",item.proposition.payload.text),el("p",`Proposition ${item.proposition.id} · ${item.proposition.payload.kind}`));
 for(const record of item.review_cards){c.append(el("span",record.evidence_reuse_candidate?"CURRENT REVIEW REFERENCES":"REVIEW REUSE BLOCKED","badge"));
 if(record.blocked_reasons.length)c.append(el("p",record.blocked_reasons.join(", ")));
 for(const review of record.reviews)c.append(el("p",`Recorded review: ${review.payload.finding} — ${review.payload.rationale}`));}
 if(!item.review_cards.length)c.append(el("p","No review card. This entry is not a verified finding."));
 const d=el("details");d.append(el("summary","Scope, revisions and evidence references"),el("pre",JSON.stringify(item,null,2)));c.append(d);results.append(c);}
 if(!data.items.length)results.append(el("p","No lexical matches. This does not establish that a matching claim is absent."));});
 content.append(input,b,results);
}
