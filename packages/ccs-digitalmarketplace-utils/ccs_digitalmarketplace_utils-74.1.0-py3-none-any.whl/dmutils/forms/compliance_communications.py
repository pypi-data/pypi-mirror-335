import re

from .fields import (
    DMRadioField,
    DMStripWhitespaceStringField,
    DMFileField,
)
from .widgets import DMTextArea
from ..documents import file_is_less_than_10mb

from flask_wtf import FlaskForm
from wtforms.validators import (
    InputRequired,
    Length,
    ValidationError
)


def word_length(limit, message):
    message = message % limit

    def _length(form, field):
        if not field.data or not limit:
            return field

        if len(field.data.split()) > limit:
            raise ValidationError(message)

    return _length


class ComplianceCommunicationCategoryForm(FlaskForm):
    def __init__(self, framework_categories, **kwargs):
        super().__init__(**kwargs)
        self.framework_categories = framework_categories

        self.category.options = [
            {
                "value": category,
                "label": category.capitalize()
            }
            for category in framework_categories
        ]

    category = DMRadioField(
        "Select the appropriate category for your message thread",
        validators=[
            InputRequired(message='You must select an option')
        ]
    )


class ComplianceCommunicationSubjectForm(FlaskForm):
    def __init__(self, data_api_client, framework_slug, supplier_id, **kwargs):
        super().__init__(**kwargs)
        self.data_api_client = data_api_client
        self.framework_slug = framework_slug
        self.supplier_id = supplier_id

    subject = DMStripWhitespaceStringField(
        "Enter the subject for the message thread",
        validators=[
            InputRequired(message="You must enter the subject for the message thread"),
            Length(max=100, message="The subject must be no more than 100 characters"),
        ]
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        valid = True

        if self.subject.data.lower() in [
            communication['subject'].lower() for communication in self.data_api_client.find_communications_iter(
                framework=self.framework_slug,
                supplier_id=self.supplier_id
            )
        ]:
            self.subject.errors.append(
                "This subject has already been used for another message thread. The subject must be unique"
            )
            valid = False

        return valid


class ComplianceCommunicationMessageForm(FlaskForm):
    message = DMStripWhitespaceStringField(
        "Enter the message",
        widget=DMTextArea(max_length_in_words=500),
        validators=[
            InputRequired(message="You must enter a message"),
            Length(max=5000, message="The message must be no more than 5000 characters"),
            word_length(500, "The message must be no more than %d words"),
        ]
    )

    attachment_file_0 = DMFileField(
        "File",
        hint='<ul class="govuk-list">'
             '<li class="govuk-hint">The file must have a maximum file size of 10MB</li>'
             '<li class="govuk-hint">The filename can only contain letters, numbers, spaces and/or underscores</li>'
             '</ul>',
        validators=[]
    )
    attachment_required_0 = DMStripWhitespaceStringField(
        "Attachment required",
        hint="Check this to include attachment 1",
        validators=[],
    )

    attachment_file_1 = DMFileField(
        "File",
        hint='<ul class="govuk-list">'
             '<li class="govuk-hint">The file must have a maximum file size of 10MB</li>'
             '<li class="govuk-hint">The filename can only contain letters, numbers, spaces and/or underscores</li>'
             '</ul>',
        validators=[]
    )
    attachment_required_1 = DMStripWhitespaceStringField(
        "Attachment required",
        hint="Check this to include attachment 2",
        validators=[],
    )

    attachment_file_2 = DMFileField(
        "File",
        hint='<ul class="govuk-list">'
             '<li class="govuk-hint">The file must have a maximum file size of 10MB</li>'
             '<li class="govuk-hint">The filename can only contain letters, numbers, spaces and/or underscores</li>'
             '</ul>',
        validators=[]
    )
    attachment_required_2 = DMStripWhitespaceStringField(
        "Attachment required",
        hint="Check this to include attachment 3",
        validators=[]
    )

    def attachments(self):
        return {
            'attachment_file_0': {
                "file": self.attachment_file_0,
                "required": self.attachment_required_0,
            },
            'attachment_file_1': {
                "file": self.attachment_file_1,
                "required": self.attachment_required_1,
            },
            'attachment_file_2': {
                "file": self.attachment_file_2,
                "required": self.attachment_required_2,
            }
        }

    def validate_attachment_file(self, valid, attachment, index):
        allowed_characters_pattern = re.compile(r'^[a-zA-Z0-9 _]*\.[a-zA-Z]+$')

        if not attachment["file"].data or not attachment["file"].data.filename:
            attachment["file"].errors.append(
                f"You must select a file for attachment {index}"
            )
            valid = False
        elif len(attachment["file"].data.filename) > 100:
            attachment["file"].errors.append(
                f"The filename for attachment {index} must be no more than 100 characters"
            )
            valid = False
        elif not allowed_characters_pattern.match(attachment["file"].data.filename):
            attachment["file"].errors.append(
                f"The filename for attachment {index} can only contain letters, numbers, spaces and/or underscores"
            )
            valid = False
        elif not file_is_less_than_10mb(attachment["file"].data):
            attachment["file"].errors.append(
                f"The file size must be less than 10MB for attachment {index}"
            )
            valid = False
        elif attachment["file"].data.filename.lower() in [
            attachment["file"].data
                and attachment["file"].data.filename
                and attachment["file"].data.filename.lower() for i, attachment in enumerate(
                self.attachments().values(), 1
            ) if index != i and attachment["required"].data
        ]:
            attachment["file"].errors.append(
                "You already have an attachment with this filename. The attachment filename must be unique"
            )
            valid = False

        return valid

    def validate(self, extra_validators=None):
        # We have to the validation manually as we only validate the required attachments
        valid = True

        if not super().validate(extra_validators):
            valid = False

        for index, attachment in enumerate(self.attachments().values(), 1):
            if attachment["required"].data:
                valid = self.validate_attachment_file(valid, attachment, index)
            else:
                attachment["file"].raw_data = None
                attachment["file"].data = None

        return valid

    def add_attachment_upload_errors(self, upload_errors):
        for index, (field, attachment) in enumerate(self.attachments().items(), 1):
            if field in upload_errors:
                attachment["file"].errors.append(
                    "Attachment %d failed to upload. Please try again." % index
                )
