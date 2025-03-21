from flask import current_app
from invenio_records_resources.services.records.components import ServiceComponent

from oarepo_doi.api import community_slug_for_credentials, create_doi, edit_doi
from invenio_base.utils import obj_or_import_string

class DoiComponent(ServiceComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mode = current_app.config.get("DATACITE_MODE")
        self.url = current_app.config.get("DATACITE_URL")
        self.mapping = current_app.config.get("DATACITE_MAPPING")
        self.specified_doi = current_app.config.get("DATACITE_SPECIFIED_ID")

        self.username = None
        self.password = None
        self.prefix = None

    def credentials(self, community):
        if not community:
            credentials = current_app.config.get(
                "DATACITE_CREDENTIALS_DEFAULT"
            )
        else:
            credentials_def = current_app.config.get("DATACITE_CREDENTIALS")

            credentials = credentials_def.get(community, None)
            if not credentials:
                credentials = current_app.config.get(
                    "DATACITE_CREDENTIALS_DEFAULT"
                )
        self.username = credentials["username"]
        self.password = credentials["password"]
        self.prefix = credentials["prefix"]

    def create(self, identity, data=None, record=None, **kwargs):
        if self.mode == "AUTOMATIC_DRAFT":
            slug = community_slug_for_credentials(
                record.parent["communities"].get("default", None)
            )
            self.credentials(slug)
            create_doi(self, record, data, None)

    def update_draft(self, identity, data=None, record=None, **kwargs):
        if self.mode == "AUTOMATIC_DRAFT" or self.mode == "ON_EVENT_DRAFT":
            slug = community_slug_for_credentials(
                record.parent["communities"].get("default", None)
            )

            self.credentials(slug)
            edit_doi(self, record)

    def update(self, identity, data=None, record=None, **kwargs):
        if (
            self.mode == "AUTOMATIC_DRAFT"
            or self.mode == "AUTOMATIC"
            or self.mode == "ON_EVENT"
            or self.mode == "ON_EVENT_DRAFT"
        ):
            slug = community_slug_for_credentials(
                record.parent["communities"].get("default", None)
            )
            self.credentials(slug)
            edit_doi(self, record)

    def publish(self, identity, data=None, record=None, draft=None, **kwargs):
        record.pids = draft.pids #todo because of excluded pids components pids are not in published record, this needs to be solved better
        if record.pids is None:
            record.pids = {}
        if self.mode == "AUTOMATIC":
            slug = community_slug_for_credentials(
                record.parent["communities"].get("default", None)
            )
            self.credentials(slug)
            create_doi(self, record, record, "publish")
        if self.mode == "AUTOMATIC_DRAFT" or self.mode == "ON_EVENT_DRAFT":
            slug = community_slug_for_credentials(
                record.parent["communities"].get("default", None)
            )
            self.credentials(slug)
            edit_doi(self, record, "publish")

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        mapping = obj_or_import_string(self.mapping[record.schema])()
        doi_value = mapping.get_doi_value(record)
        if doi_value is not None:
            mapping.remove_doi_value(draft)
