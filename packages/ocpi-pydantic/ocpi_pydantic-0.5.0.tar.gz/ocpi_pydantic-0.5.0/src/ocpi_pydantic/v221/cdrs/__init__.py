from pydantic import AwareDatetime, BaseModel, Field

from ocpi_pydantic.v221.base import OcpiBaseResponse
from ocpi_pydantic.v221.enum import OcpiCrdDeminsionTypeEnum, OcpiTokenTypeEnum



class OcpiCdrToken(BaseModel):
    '''
    OCPI 10.4.5. CdrToken class

    - `uid`:  
        Unique ID by which this Token can be identified.
        This is the field used by the CPO’s system (RFID reader on the Charge Point) to
        identify this token.
        Currently, in most cases: type=RFID, this is the RFID hidden ID as read by the
        RFID reader, but that is not a requirement.
        If this is a type=APP_USER Token, it will be a unique, by the eMSP, generated
        ID.
    - `contract_id`:
        Uniquely identifies the EV driver contract token within the eMSP’s platform (and
        suboperator platforms). Recommended to follow the specification for eMA ID
        from "eMI3 standard version V1.0" (http://emi3group.com/documents-links/)
        "Part 2: business objects."
    '''

    country_code: str = Field(description="ISO-3166 alpha-2 country code of the MSP that 'owns' this Token.", min_length=2, max_length=2)
    party_id: str = Field(description="ID of the eMSP that 'owns' this Token (following the ISO-15118 standard).", min_length=3, max_length=3)
    uid: str = Field(description='Unique ID by which this Token can be identified.', max_length=36)
    type: OcpiTokenTypeEnum = Field(description='Type of the token')
    contract_id: str = Field(description='Uniquely identifies the EV driver contract token within the eMSP’s platform (and suboperator platforms).')



class OcpiCdrDimension(BaseModel):
    '''
    OCPI 10.4.2. CdrDimension class

    - `start_date_time`:
        Start timestamp of the charging period. A period ends when the next period
        starts. The last period ends when the session ends.
    '''
    type : OcpiCrdDeminsionTypeEnum = Field(description='Type of CDR dimension.')
    volume: float = Field(description='Volume of the dimension consumed, measured according to the dimension type.')



class OcpiChargingPeriod(BaseModel):
    '''
    OCPI 10.4.6. ChargingPeriod class

    A Charging Period consists of a start timestamp and a list of possible values that influence this period, for example: amount of energy charged this period, maximum current during this period etc.

    - `start_date_time`:
        Start timestamp of the charging period. A period ends when the next period
        starts. The last period ends when the session ends.
    - `tariff_id`:
        Unique identifier of the Tariff that is relevant for this Charging Period. If not
        provided, no Tariff is relevant during this period.
    '''
    start_date_time : AwareDatetime = Field(description='Start timestamp of the charging period.')
    dimensions: list[OcpiCdrDimension] = Field(description='List of relevant values for this charging period.')
    tariff_id: str | None = Field(None, description='Unique identifier of the Tariff that is relevant for this Charging Period.', max_length=36)
