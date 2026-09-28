"""Explicit wiring; no dynamic plugin loading and no pillar-to-pillar imports."""

from statement_ledger.core.ledger import Ledger as CoreLedger
from statement_ledger.core.validation import ValidatorRegistry
from statement_ledger.core.validators import validate_person, validate_rights
from statement_ledger.infrastructure.providers.validation import validate_decision_run
from statement_ledger.infrastructure.settings import Settings
from statement_ledger.infrastructure.sqlite_store import Store
from statement_ledger.pillars.claims.validators import (
    validate_claim_card,
    validate_claim_family,
    validate_occurrence,
    validate_proposition,
)
from statement_ledger.pillars.discovery.validators import (
    validate_appearance,
    validate_coverage_run,
    validate_event,
    validate_observation,
)
from statement_ledger.pillars.evidence.validators import (
    validate_correction,
    validate_evidence,
    validate_review,
)
from statement_ledger.pillars.ledger.projection import person_ledger
from statement_ledger.pillars.media.validators import validate_asset
from statement_ledger.pillars.speech.validators import (
    validate_localization_run,
    validate_speaker_mapping,
    validate_speaker_profile,
    validate_transcript,
    validate_utterance,
)


def validators():
    registry = ValidatorRegistry()
    registry.register("appearance", validate_appearance)
    registry.register("asset", validate_asset)
    registry.register("claim_card", validate_claim_card)
    registry.register("claim_family", validate_claim_family)
    registry.register("correction", validate_correction)
    registry.register("coverage_run", validate_coverage_run)
    registry.register("decision_run", validate_decision_run)
    registry.register("event", validate_event)
    registry.register("evidence", validate_evidence)
    registry.register("localization_run", validate_localization_run)
    registry.register("observation", validate_observation)
    registry.register("occurrence", validate_occurrence)
    registry.register("person", validate_person)
    registry.register("proposition", validate_proposition)
    registry.register("review", validate_review)
    registry.register("rights", validate_rights)
    registry.register("speaker_mapping", validate_speaker_mapping)
    registry.register("speaker_profile", validate_speaker_profile)
    registry.register("transcript", validate_transcript)
    registry.register("utterance", validate_utterance)
    return registry


class Ledger(CoreLedger):
    def __init__(self, store: Store) -> None:
        self.settings: Settings | None = None
        super().__init__(store, validators())

    def person_ledger(self, person_id):
        return person_ledger(self, person_id)
