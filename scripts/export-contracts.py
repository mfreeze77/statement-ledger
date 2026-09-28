from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from statement_ledger.models import KINDS
from statement_ledger.api import create_app
out=ROOT/"contracts";out.mkdir(exist_ok=True)
for kind,model in KINDS.items():
    (out/f"{kind}.schema.json").write_text(json.dumps(model.model_json_schema(),indent=2,sort_keys=True)+"\n")
app=create_app(":memory:","contract-generation-only-not-a-deployment-secret")
(out/"openapi.json").write_text(json.dumps(app.openapi(),indent=2,sort_keys=True)+"\n")

from statement_ledger.claim_seeds import ClaimSeed
from statement_ledger.acceleration_models import ProfileConfig, LocalizationConfig
for name, model in (("claim-seed",ClaimSeed),("profile-config",ProfileConfig),("localization-config",LocalizationConfig)):
    (out/f"{name}.schema.json").write_text(json.dumps(model.model_json_schema(),indent=2,sort_keys=True)+"\n")
