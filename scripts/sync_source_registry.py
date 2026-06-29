# scripts/sync_source_registry.py
from app.services.source_registry_service import SourceRegistryService

service = SourceRegistryService()

service.register_source(
    source_id="bmg-web",
    name="Bundesministerium für Gesundheit",
    source_type="web",
    description="Publications from the Federal Ministry of Health",
    enabled=False,
    metadata={
        "urls": [],
        "allowed_domains": ["bundesgesundheitsministerium.de"],
        "document_type": "public-web",
        "topics": ["healthcare-policy"],
    },
)
