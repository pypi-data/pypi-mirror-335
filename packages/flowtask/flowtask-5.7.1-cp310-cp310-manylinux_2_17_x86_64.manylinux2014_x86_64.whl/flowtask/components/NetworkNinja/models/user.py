from typing import List, Optional
from datetime import datetime
from datamodel import BaseModel, Field
from .abstract import AbstractPayload
from .organization import Organization
from .market import Market
from .district import District
from .region import Region
from .client import Client


class Role(AbstractPayload):
    role_id: int = Field(primary_key=True, required=True)
    client_id: int = Field(primary_key=True, alias="role_client_id")
    orgid: int = Field(alias="role_org_id")
    role_name: str = Field(alias='name')
    visit_id: int = Field(alias="role_visit_id")

    class Meta:
        strict = True
        as_objects = True
        name = 'roles'
        schema: str = 'networkninja'

class User(AbstractPayload):
    """
    User Model.

    Represents a user in the system.

    Example:
        {
            "user_id": 1,
            "username": "admin",
            "employee_number": 1234,
            "first_name": "John",
            "last_name": "Doe",
            "email": "
            "mobile_number": "123-456-7890",
            "role_id": 1,
            "role_name": "Admin",
            "address": "1234 Elm St",
            "city": "Springfield",
            "state_code": "IL",
            "zipcode": "62704",
            "latitude": 39.781721,
            "longitude": -89.650148,
        }
    """
    user_id: int = Field(primary_key=True, required=True)
    username: str = Field(required=True)
    employee_number: int
    first_name: str
    last_name: str
    display_name: str
    email_address: str = Field(alias="email")
    mobile_number: str
    position_id: Optional[str]
    role_id: Role
    role_name: str
    address: str
    city: str
    state_code: str = Field(alias="state_name")
    zipcode: str
    latitude: Optional[float]
    longitude: Optional[float]
    physical_country: Optional[str]
    is_active: bool = Field(required=True, default=True)
    orgid: List[Organization]
    # hierarchy
    region_name: List[str] = Field(alias='regions')
    district_name: List[str] = Field(alias='districts')
    market_name: List[str] = Field(alias='markets')
    client_name: List[str] = Field(alias='client_names')
    client_id: List[int] = Field(alias='client_ids')

    class Meta:
        strict = True
        as_objects = True
        name = 'users'
        schema: str = 'networkninja'

    def __post_init__(self):
        super().__post_init__()
        if self.role_id:
            self.role_id.role_name = self.role_name
        if not self.display_name:
            self.display_name = f'{self.first_name} {self.last_name}'
        if self.display_name and not self.first_name:
            self.first_name, self.last_name = self.display_name.split(' ')


class StaffingUser(AbstractPayload):
    user_id: int = Field(primary_key=True, required=True, alias="id")
    username: str = Field(required=True)
    employee_number: str
    first_name: str
    last_name: str
    display_name: str
    email: str = Field(alias="email_address")
    mobile_number: str
    address: str
    city: str
    state_name: str = Field(alias="state")
    physical_country: str
    zipcode: str
    position_id: Optional[str]
    roles: List[Role] = Field(default_factory=list)
    markets: List[Market] = Field(default_factory=list)
    districts: List[District] = Field(default_factory=list)
    regions: List[Region] = Field(default_factory=list)
    orgid: List[int]
    clients: Optional[List[Client]] = Field(alias="client_ids")
    client_names: List[str]
    role_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    custom_fields: List[dict[str, str]]
    onboarding: datetime
    is_active: bool = Field(required=True, default=True)

    class Meta:
        strict = True
        as_objects = True
        name = 'staffing_users'
        schema: str = 'networkninja'

    def __post_init__(self):
        super().__post_init__()
        if not self.display_name:
            self.display_name = f'{self.first_name} {self.last_name}'
        if self.display_name and not self.first_name:
            self.first_name, self.last_name = self.display_name.split(' ')

    async def _sync_object(self, conn):
        """
        Sync Staffing User and dependencies.
        """
        # Sync Roles
        for role in self.roles:
            try:
                role.client_id = self.client_id
                await role.sync()
            except Exception as e:
                self._logger.error(f"Error syncing Role: {e}")
        # Sync Markets
        markets = []
        for market in self.markets:
            market.market_id = int(market.market_id)
            markets.append(market)
        if markets:
            await markets[0].update_many(
                markets
            )
