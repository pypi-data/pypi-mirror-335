from typing import ClassVar

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from ocpi_pydantic.v221.base import OcpiBaseResponse, OcpiPrice
from ocpi_pydantic.v221.cdrs import OcpiCdrToken, OcpiChargingPeriod
from ocpi_pydantic.v221.enum import OcpiAuthMethodEnum, OcpiChargingPreferencesResponseEnum, OcpiProfileTypeEnum, OcpiSessionStatusEnum



class OcpiSession(BaseModel):
    '''
    OCPI 9.3.1. Session Object

    - `start_date_time`:  
        The timestamp when the session became ACTIVE in the Charge
        Point.
        When the session is still PENDING, this field SHALL be set to the
        time the Session was created at the Charge Point. When a Session
        goes from PENDING to ACTIVE, this field SHALL be updated to the
        moment the Session went to ACTIVE in the Charge Point.
    - `auth_method`:
        Method used for authentication. This might change during a
        session, for example when the session was started with a
        reservation: ReserveNow: `COMMAND`. When the driver arrives and
        starts charging using a Token that is whitelisted: `WHITELIST`.
    - `authorization_reference`:
        Reference to the authorization given by the eMSP. When the eMSP
        provided an `authorization_reference` in either: real-time
        authorization, StartSession or ReserveNow this field SHALL
        contain the same value. When different
        `authorization_reference` values have been given by the
        eMSP that are relevant to this Session, the last given value SHALL
        be used here.
    - `evse_uid`:
        EVSE.uid of the EVSE of this Location on which the charging
        session is/was happening. Allowed to be set to: `#NA` when this
        session is created for a reservation, but no EVSE yet assigned to
        the driver.
    - `connector_id`:
        Connector.id of the Connector of this Location where the charging
        session is/was happening. Allowed to be set to: `#NA` when this
        session is created for a reservation, but no connector yet assigned
        to the driver.
    - `total_cost`:
        The total cost of the session in the specified currency. This is the
        price that the eMSP will have to pay to the CPO. A total_cost of
        0.00 means free of charge. When omitted, i.e. no price information
        is given in the Session object, it does not imply the session is/was
        free of charge.
    
    Note:

    Different `authorization_reference` values might happen when for example a ReserveNow had a different
    `authorization_reference` then the value returned by a real-time authorization.
    '''

    country_code: str = Field(description="ISO-3166 alpha-2 country code of the CPO that 'owns' this Session.", min_length=2, max_length=2)
    party_id: str = Field(description="ID of the CPO that 'owns' this Session (following the ISO-15118 standard).", min_length=3, max_length=3)
    id: str = Field(description='The unique id that identifies the charging session in the CPO platform.', max_length=36)
    start_date_time: AwareDatetime = Field(description='The timestamp when the session became ACTIVE in the Charge Point.')
    end_date_time: AwareDatetime | None = Field(None, description='The timestamp when the session was completed/finished, charging might have finished before the session ends, for example: EV is full, but parking cost also has to be paid.')
    kwh: int = Field(description='How many kWh were charged.')
    cdr_token: OcpiCdrToken = Field(description='Token used to start this charging session, including all the relevant information to identify the unique token.')
    auth_method: OcpiAuthMethodEnum = Field(description='Method used for authentication.')
    authorization_reference: str | None = Field(None, description='Reference to the authorization given by the eMSP.', max_length=36)
    location_id: str = Field(description='Location.id of the Location object of this CPO, on which the charging session is/was happening.', max_length=36)
    evse_uid : str = Field(description='EVSE.uid of the EVSE of this Location on which the charging session is/was happening.', max_length=36)
    connector_id : str = Field(description='Connector.id of the Connector of this Location where the charging session is/was happening.', max_length=36)
    meter_id: str | None = Field(None, description='Optional identification of the kWh meter.', max_length=255)
    currency: str = Field(description='ISO 4217 code of the currency used for this session.', max_length=3)
    charging_periods: list[OcpiChargingPeriod] = Field([], description='An optional list of Charging Periods that can be used to calculate and verify the total cost.')
    total_cost: OcpiPrice | None = Field(None, description='The total cost of the session in the specified currency.')
    status: OcpiSessionStatusEnum = Field(description='The status of the session.')
    last_updated: AwareDatetime = Field(description='Timestamp when this Session was last updated (or created).')

    _examples: ClassVar[list[dict]] = [
        { # Simple Session example of just starting a session
            "country_code": "NL",
            "party_id": "STK",
            "id": "101",
            "start_date_time": "2020-03-09T10:17:09Z",
            "kwh": 0.0,
            "cdr_token": {"uid": "123abc", "type": "RFID", "contract_id": "NL-TST-C12345678-S"},
            "auth_method": "WHITELIST",
            "location_id": "LOC1",
            "evse_uid": "3256",
            "connector_id": "1",
            "currency": "EUR",
            "total_cost": {"excl_vat": 2.5},
            "status": "PENDING",
            "last_updated": "2020-03-09T10:17:09Z"
        },
        { # Simple Session example of a short finished session
            "country_code": "BE",
            "party_id": "BEC",
            "id": "101",
            "start_date_time": "2015-06-29T22:39:09Z",
            "end_date_time": "2015-06-29T23:50:16Z",
            "kwh": 41.00,
            "cdr_token": {"uid": "123abc", "type": "RFID", "contract_id": "NL-TST-C12345678-S"},
            "auth_method": "WHITELIST",
            "location_id": "LOC1",
            "evse_uid": "3256",
            "connector_id": "1",
            "currency": "EUR",
            "charging_periods": [
                {
                    "start_date_time": "2015-06-29T22:39:09Z",
                    "dimensions": [{"type": "ENERGY", "volume": 120}, {"type": "MAX_CURRENT", "volume": 30}]
                },
                {
                    "start_date_time": "2015-06-29T22:40:54Z",
                    "dimensions": [{"type": "ENERGY", "volume": 41000}, {"type": "MIN_CURRENT", "volume": 34}]
                },
                {
                    "start_date_time": "2015-06-29T23:07:09Z",
                    "dimensions": [{"type": "PARKING_TIME", "volume": 0.718}],
                    "tariff_id": "12"
                }
            ],
            "total_cost": {"excl_vat": 8.50, "incl_vat": 9.35},
            "status": "COMPLETED",
            "last_updated": "2015-06-29T23:50:17Z"
        },
    ]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})




class OcpiSessionListResponse(OcpiBaseResponse):
    data: list[OcpiSession]

    _examples: ClassVar[dict] = [{
        'data': [OcpiSession._examples[0]], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiSessionResponse(OcpiBaseResponse):
    data: OcpiSession

    _examples: ClassVar[dict] = [{
        'data': OcpiSession._examples[0], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiChargingPreferences(BaseModel):
    '''
    OCPI 9.3.2. ChargingPreferences Object
    
    Contains the charging preferences of an EV driver.

    - `profile_type `:  
        Type of Smart Charging Profile selected by the driver. The ProfileType has to be
        supported at the Connector and for every supported ProfileType, a Tariff MUST
        be provided. This gives the EV driver the option between different pricing
        options.
    - `departure_time`:
        Expected departure. The driver has given this Date/Time as expected departure
        moment. It is only an estimation and not necessarily the Date/Time of the actual
        departure.
    - `energy_need`:
        Requested amount of energy in kWh. The EV driver wants to have this amount
        of energy charged.
    - `discharge_allowed`:
        The driver allows their EV to be discharged when needed, as long as the other
        preferences are met: EV is charged with the preferred energy (`energy_need`)
        until the preferred departure moment (`departure_time`). Default if omitted:
        **false**
    '''
    profile_type: OcpiProfileTypeEnum = Field(description='Type of Smart Charging Profile selected by the driver.ß')
    departure_time: AwareDatetime | None = Field(None, description='Expected departure.')
    energy_need: float | None = Field(None, description='Requested amount of energy in kWh.')
    discharge_allowed: bool = Field(False, description='The driver allows their EV to be discharged when needed.')



class OcpiChargingPreferencesResponse(OcpiBaseResponse):
    data: OcpiChargingPreferencesResponseEnum

    _examples: ClassVar[dict] = [{
        'data': OcpiSession._examples[0], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})
