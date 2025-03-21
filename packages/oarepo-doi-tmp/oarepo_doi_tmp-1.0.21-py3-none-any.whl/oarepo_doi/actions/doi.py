from flask import current_app
from invenio_base.utils import obj_or_import_string
from marshmallow.exceptions import ValidationError
from oarepo_requests.actions.generic import OARepoAcceptAction, OARepoSubmitAction

from oarepo_doi.api import community_slug_for_credentials, create_doi, delete_doi

class AssignDoiAction(OARepoAcceptAction):
    log_event = True

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

class CreateDoiAction(AssignDoiAction):


    def execute(self, identity, uow, *args, **kwargs):
        topic = self.request.topic.resolve()
        slug = community_slug_for_credentials(topic.parent["communities"].get("default", None))

        self.credentials(slug)

        #todo - only public?
        if topic.is_draft:
            create_doi(self, topic, topic, None)
        else:
            create_doi(self, topic, topic, "publish")
        super().execute(identity, uow)

class DeleteDoiAction(AssignDoiAction):

    def execute(self, identity, uow, *args, **kwargs):
        topic = self.request.topic.resolve()
        slug = community_slug_for_credentials(topic.parent["communities"].get("default", None))

        self.credentials(slug)

        delete_doi(self, topic)

        super().execute(identity, uow)

class RegisterDoiAction(AssignDoiAction):

    def execute(self, identity, uow, *args, **kwargs):
        topic = self.request.topic.resolve()
        slug = community_slug_for_credentials(topic.parent["communities"].get("default", None))

        self.credentials(slug)

        create_doi(self, topic, topic, None)

        super().execute(identity, uow)
class ValidateDataForDoiAction(OARepoSubmitAction):
    log_event = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mapping = current_app.config.get("DATACITE_MAPPING")

    def execute(self, identity, uow, *args, **kwargs):
        topic = self.request.topic.resolve()
        mapping = obj_or_import_string(self.mapping[topic.schema])()
        errors = mapping.metadata_check(topic)
        if len(errors) > 0:
            raise ValidationError(
                message=errors
            )

        super().execute(identity, uow)
