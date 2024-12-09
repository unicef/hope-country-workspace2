from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Endpoint:
    base: str
    deduplication_set: str = "deduplication_sets/"
    deduplication_set_detail: str = "deduplication_sets/{deduplication_set_id}/"
    duplicate: str = "deduplication_sets/{deduplication_set_id}/duplicates/"
    ignored: str = "deduplication_sets/{deduplication_set_id}/ignored/{resource_type}/"
    image: str = "deduplication_sets/{deduplication_set_id}/images/"
    image_detail: str = "deduplication_sets/{deduplication_set_id}/images/{image_id}/"
    image_bulk: str = "deduplication_sets/{deduplication_set_id}/images_bulk/"
    image_bulk_clear: str = "deduplication_sets/{deduplication_set_id}/images_bulk/clear/"
    process: str = "deduplication_sets/{deduplication_set_id}/process/"

    def __post_init__(self):
        if not self.base.startswith("https://"):
            raise ValueError(f"Invalid base URL: '{self.base}'. Must start with 'https://'.")
