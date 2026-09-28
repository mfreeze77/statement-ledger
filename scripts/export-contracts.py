"""Generate contracts without bootstrapping or touching an operator database."""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from statement_ledger.application.api import create_app  # noqa: E402
from statement_ledger.contracts.acceleration import LocalizationConfig, ProfileConfig  # noqa: E402
from statement_ledger.contracts.models import KINDS  # noqa: E402
from statement_ledger.contracts.runtime import (  # noqa: E402
    Clip,
    ImportTranscript,
    JevDecision,
    JobRequest,
    Localize,
    RequeueJob,
    Transcribe,
)
from statement_ledger.infrastructure.migrations import migrate  # noqa: E402
from statement_ledger.infrastructure.settings import Settings  # noqa: E402
from statement_ledger.pillars.claims.seeds import ClaimSeed  # noqa: E402

out = ROOT / "contracts"
out.mkdir(exist_ok=True)
for kind, model in KINDS.items():
    (out / f"{kind}.schema.json").write_text(
        json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
with tempfile.TemporaryDirectory() as directory:
    settings = Settings(data_root=Path(directory))
    migrate(settings.database)
    app = create_app(settings=settings, token="contract-generation-only-not-a-deployment-secret")
    (out / "openapi.json").write_text(
        json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
for name, model in (
    ("claim-seed", ClaimSeed),
    ("profile-config", ProfileConfig),
    ("localization-config", LocalizationConfig),
):
    (out / f"{name}.schema.json").write_text(
        json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
(out / "runtime").mkdir(exist_ok=True)
for model in (JobRequest, ImportTranscript, Localize, Clip, JevDecision, Transcribe, RequeueJob):
    (out / "runtime" / f"{model.__name__}.schema.json").write_text(
        json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
