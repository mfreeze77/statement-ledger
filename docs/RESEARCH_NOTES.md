# Research and source-verification boundaries

Review date: 2026-09-27. These notes support integration design; all implementation choices beyond the documented interfaces are proposals or local code behavior.

## First-party documentation inspected for this build

| Source | Design fact checked | Reference |
|---|---|---|
| YouTube | Search parameters/pagination, channel discovery, and separate caption permissions | https://developers.google.com/youtube/v3/docs/search/list ; https://developers.google.com/youtube/v3/docs/captions/download |
| YouTube policies | Discovery does not confer unrestricted downloading/storage permissions | https://developers.google.com/youtube/terms/developer-policies |
| Google Fact Check | Claims search is a paginated query API | https://developers.google.com/fact-check/tools/api/reference/rest/v1alpha1/claims/search |
| GDELT GQG | Nested quote records with pre/post snippets and JSONL compressed archives | https://blog.gdeltproject.org/announcing-the-global-quotation-graph/ |
| GDELT TV API | Historical documentation exposes search and coverage interfaces; metrics are not speaker counts | https://blog.gdeltproject.org/gdelt-2-0-television-api-debuts/ |
| Quotebank | Quotation-centric and article-centric exports differ; speaker assignments have uncertainty | https://zenodo.org/records/4277311 |
| Fact-Check Insights | JSON/CSV formats, original publisher scales, appearance fields | https://www.factcheckinsights.org/guide |
| AAPB | Metadata interface and separate research transcript access | https://github.com/WGBH-MLA/AAPB2 |
| Internet Archive | Metadata retrieval and item file inventory | https://archive.org/developers/md-read.html |
| Media Cloud | Public search API guide and official tooling | https://www.mediacloud.org/documentation/search-api-guide |
| TVEyes | Commercial API/data integration offering, not an account entitlement | https://www.tveyes.com/api-partners/ |
| Critical Mention | Commercial API integration offering | https://www.criticalmention.com/api/ |
| Faster Whisper | Local speech-transcription library interface | https://github.com/SYSTRAN/faster-whisper |
| Pyannote Audio | Diarization produces local speaker assignments; named identity is a separate task | https://github.com/pyannote/pyannote-audio |
| WhisperX | Alignment/diarization workflow and documented limitations; study/reference, not a bundled dependency | https://github.com/m-bain/whisperX |
| GitHub | Creating a new repository, distinct from adding files to an existing one | https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository |

## Not verified

No commercial API schema was inferred from a marketing page. No working account subscription is assumed. No source API is marked live-connected. The prior proposed GDELT Visual Explorer deep link could not be verified; its worksheet explicitly asks for current documentation rather than presenting an invented endpoint. Other publisher pages remain discovery/reference pointers until intake tests are complete.

The runtime could not resolve the GDELT archive and AAPB metadata hosts. The same environment could not resolve the package registry for `uv lock`. These are environment failures, not evidence that the public sources are offline. No fresh source data or model weights were downloaded, and no universal lock file was fabricated.

## Third-party software handling

The repository contains original reference code and synthetic fixtures, not copied third-party source trees or media. External software/model licenses are separate from this repository's software-license notice. Optional model integration requires a reviewed exact version, model revision, runtime configuration and license before deployment. No supplied recording, transcript or model should inherit this repository's license by assumption.
