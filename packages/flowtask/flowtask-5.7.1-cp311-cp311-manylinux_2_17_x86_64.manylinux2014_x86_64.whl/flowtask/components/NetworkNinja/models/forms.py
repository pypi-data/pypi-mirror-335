from typing import List, Optional, Union
from datetime import datetime
from datamodel import BaseModel, Field
from .abstract import AbstractPayload
from .organization import Organization
from .client import Client
from .store import CustomStoreField, Store, StoreType
from .user import User, StaffingUser
from .region import Region
from .account import Account


class Condition(BaseModel):
    """
    Defines a Condition, a condition for a Logic Group.
    Example:
        {
            "condition_id": 1835,
            "condition_logic": "EQUALS",
            "condition_comparison_value": "Regular",
            "condition_question_reference_id": 48,
            "condition_option_id": 4308
        }
    """
    condition_id: int = Field(primary_key=True, required=True)
    condition_logic: str = Field(required=True)
    condition_comparison_value: str = Field(required=True)
    condition_question_reference_id: str
    condition_option_id: str


class Validation(BaseModel):
    """
    Defines a Validation, a validation rule for a question.
    Example:
        {
            "validation_id": 43,
            "validation_type": "responseRequired",
            "validation_logic": null,
            "validation_comparison_value": null,
            "validation_question_reference_id": null
        }
    """
    validation_id: int = Field(primary_key=True, required=True)
    validation_type: str = Field(required=True)
    validation_logic: str
    validation_comparison_value: str
    validation_question_reference_id: str
    condition_option_id: str


class LogicGroup(BaseModel):
    """
    Defines a Logic Group, a group of questions in a Form.
    Example:
        {
            "logic_group_id": 1706,
            "conditions": [
                {
                    "condition_id": 1835,
                    "condition_logic": "EQUALS",
                    "condition_comparison_value": "Regular",
                    "condition_question_reference_id": 48,
                    "condition_option_id": 4308
                }
            ]
        }
    """
    logic_group_id: int = Field(primary_key=True, required=True)
    conditions: List[Condition]


class Question(BaseModel):
    """
    Defines a Question, a single question in a Form.
    Example:
        {
            "question_id": 48,
            "question_column_name": "8501",
            "question_description": "Purpose of Visit",
            "question_logic_groups": [],
            "validations": [
                {
                    "validation_id": 43,
                    "validation_type": "responseRequired",
                    "validation_logic": null,
                    "validation_comparison_value": null,
                    "validation_question_reference_id": null
                }
            ]
        }
    """
    question_id: int = Field(primary_key=True, required=True)
    question_column_name: Union[str, int] = Field(required=True)
    question_description: str = Field(required=True)
    question_logic_groups: List[LogicGroup]
    validations: List[Validation]

class QuestionBlock(BaseModel):
    """
    Defines a Question Block, a collection of questions in a Form.

    Example:
        {
            "question_block_id": 9,
            "question_block_type": "simple",
            "question_block_logic_groups": [],
            "questions": []
        }
    """
    block_id: int = Field(primary_key=True, required=True, alias="question_block_id")
    block_type: str = Field(alias="question_block_type")
    block_logic_groups: List[dict] = Field(alias="question_block_logic_groups")
    questions: List[dict]

class FormDefinition(AbstractPayload):
    """
    Defines a Form (recap) definition.
    """
    formid: int = Field(primary_key=True, required=True)
    client_id: Client = Field(required=True, primary_key=True)
    client_name: str
    form_name: str
    description: str = Field(alias='form_description')
    active: bool = Field(default=True)
    is_store_stamp: bool = Field(default=True)
    created_on: datetime
    updated_on: datetime
    orgid: Organization
    question_blocks: Optional[List[QuestionBlock]] = Field(default_factory=list)

    class Meta:
        strict = True
        as_objects = True
        name = 'forms'
        schema: str = 'networkninja'

    def __post_init__(self):
        super().__post_init__()
        if not self.description:
            self.description = self.form_name
        if self.client_id:
            self.client_id.client_name = self.client_name
            self.client_id.orgid = self.orgid

class Form(AbstractPayload):
    """
    Reference to a Form:
    """
    formid: int = Field(primary_key=True, required=True)
    form_name: Optional[str]
    active: bool = Field(default=True)
    client_id: Client
    client_name: str
    orgid: Organization

    class Meta:
        strict = True
        as_objects = True
        name = 'forms'
        schema: str = 'networkninja'

    def __post_init__(self):
        super().__post_init__()
        if self.client_id:
            self.client_id.client_name = self.client_name
            self.client_id.orgid = self.orgid

    async def on_sync(self):
        """
        Sync the form with the database.
        """
class FormMetadata(AbstractPayload):
    """
    Defines a Form Metadata, a single question from a Form.

    Example:
        {
            "column_name": "8452",
            "description": "Please provide a photo of the starting odometer reading",
            "is_active": true,
            "data_type": "FIELD_IMAGE_UPLOAD",
            "formid": 1,
            "form_name": "Territory Manager Visit Form TEST",
            "client_id": 59,
            "client_name": "TRENDMICRO",
            "orgid": 77
        }
    """
    # Column ID is not returned by Form Metadata payload but Form Data.
    column_id: int
    formid: Form = Field(primary_key=True, required=True)
    client_id: Client = Field(primary_key=True, required=True)
    column_name: Union[str, int] = Field(primary_key=True, required=True)
    description: str
    data_type: str = Field(required=True, alias='data_type')
    form_name: str
    is_active: bool = Field(required=True, default=True)
    client_name: str
    orgid: Organization = Field(required=True)

    class Meta:
        strict = True
        as_objects = True
        name = 'form_metadata'
        schema: str = 'networkninja'

    def __post_init__(self):
        super().__post_init__()
        self.formid.form_name = self.form_name
        if self.client_id:
            self.client_id.client_name = self.client_name
            self.client_id.orgid = self.orgid
        if self.formid:
            self.formid.client_id = self.client_id
            self.formid.client_name = self.client_name
            self.formid.orgid = self.orgid
            self.formid.form_name = self.form_name
            self.formid.active = self.is_active


class FormResponse(BaseModel):
    """
    Defines a Form Response, a response to a Form.

    Example:
        {
            "event_id": 10516,
            "column_name": 8550,
            "data": "Arturo",
            "question_shown_to_user": true,
            "column_id": "150698"
        }
    """
    formid: int = Field(primary_key=True)
    form_id: int = Field(primary_key=True)
    column_name: str = Field(primary_key=True)
    event_id: int
    data: Union[str, None]
    question_shown_to_user: bool = Field(default=True)
    column_id: str
    client_id: int
    orgid: int

    class Meta:
        name: str = 'form_responses'
        schema: str = 'networkninja'


class FormData(AbstractPayload):
    """
    Defines a Form Data, a collection of responses to a Form.

    Example:
        {
            "form_data_id": 1,
            "formid": 1,
            "client_id": 59,
            "orgid": 77,
            "store_id": 1,
            "store_name": "Best Buy 4350",
            "user_id": 1,
            "user_name": "Arturo",
            "created_at": "2025-02-01T00:00:00-06:00",
            "updated_at": "2025-02-01T00:00:00-06:00",
            "form_responses": [
                {
                    "column_name": "8550",
                    "data": "Arturo",
                    "question_shown_to_user": true,
                    "column_id": "150698"
                }
            ]
        }
    """
    form_id: int = Field(primary_key=True, required=True)
    formid: int = Field(primary_key=True, required=True)
    previous_form_id: int
    current_form_id: int
    event_id: int = Field(required=False)
    version: str
    creation_timestamp: Optional[datetime]
    start_lat: Optional[float]
    start_lon: Optional[float]
    end_lat: Optional[float]
    end_lon: Optional[float]
    visit_timestamp: Optional[datetime]
    updated_timestamp: Optional[datetime]
    project_id: int = Field(alias='program_id')
    time_in_local: Union[datetime, str]
    time_in: datetime
    visit_start_local: Optional[datetime]
    visit_end_local: Optional[datetime]
    time_out_local: Union[datetime, str]
    time_out: datetime
    device_model: str
    visitor_id: int
    visitor_username: str
    visitor_name: str
    visitor_email: str
    visitor_mobile_number: str
    visitor_geography_timezone: str
    user_id: StaffingUser
    position_id: str  # TODO: validate position ID
    store_visits_category: int
    visit_status: str
    ad_hoc: bool = Field(required=True, default=False)
    visitor_role: str
    account_id: int
    account_name: str
    retailer: str
    store_number: Store = Field(alias="store_id")
    store_name: str
    store_type_id: int
    store_type_name: str
    store_timezone: str
    store_is_active: bool = Field(default=True)
    # hierarchy:
    store_market_id: int
    store_market_name: str
    store_city: str
    store_zipcode: str
    region_id: int
    region_name: str
    district_id: int
    district_name: str
    market_id: int
    market_name: str
    client_id: int = Field(required=True)
    client_name: str
    orgid: int = Field(required=True)
    field_responses: List[FormResponse]
    store_custom_fields: List[CustomStoreField]
    manager_role: str

    class Meta:
        strict = False
        as_objects = True
        name = 'form_data'
        schema: str = 'networkninja'

    def __post_init__(self):
        # Extract the date from visit_timestamp (as string) and concatenate with time_in_local:
        super().__post_init__()
        # if isinstance(self.time_in_local, str):
        #     _visit_date = self.visit_timestamp.strftime('%Y-%m-%d')
        #     self.time_in_local = datetime.strptime(_visit_date + ' ' + self.time_in_local, '%Y-%m-%d %H:%M %p')
        #     self.time_out_local = datetime.strptime(_visit_date + ' ' + self.time_out_local, '%Y-%m-%d %H:%M %p')
        if self.store_custom_fields:
            for st in self.store_custom_fields:
                st.orgid = self.orgid
        # Saving the Form Definition:
        # if self.visitor_id:
        #     args = {
        #         'user_id': self.visitor_id,
        #         'username': self.visitor_username,
        #         'display_name': self.visitor_name,
        #         'email_address': self.visitor_email,
        #         'mobile_number': self.visitor_mobile_number,
        #         'position_id': self.position_id,
        #         'role_name': self.visitor_role,
        #     }
        #     self.user_id = StaffingUser(**args)
        # Definition of Store associated
        if self.store_number:
            if isinstance(self.store_number, int):
                try:
                    self.store_number = Store(store_number=self.store_number)
                except Exception as e:
                    print('Error in creating Store instance:', e)
            self.store_number.store_name = self.store_name
            self.store_number.city = self.store_city
            self.store_number.zipcode = self.store_zipcode
            self.store_number.account_id = self.account_id
            self.store_number.account_name = self.account_name
            if self.store_type_id:
                self.store_number.store_type_id = StoreType(
                    store_type_id=self.store_type_id,
                    store_type=self.store_type_name,
                    description=self.store_type_name,
                    client_id=self.client_id,
                    client_name=self.client_name
                )
            self.store_number.store_timezone = self.store_timezone
            self.store_number.store_is_active = self.store_is_active
            # Client info:
            self.store_number.client_id = self.client_id
            self.store_number.client_name = self.client_name
            self.store_number.orgid = self.orgid
            self.store_number.custom_fields = self.store_custom_fields
