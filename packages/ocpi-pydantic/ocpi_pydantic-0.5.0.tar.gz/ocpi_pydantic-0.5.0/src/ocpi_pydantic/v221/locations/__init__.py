from typing import ClassVar

from ocpi_pydantic.v221.enum import OcpiImageCategoryEnum
from pydantic import BaseModel, ConfigDict, Field, HttpUrl



class OcpiImage(BaseModel):
    '''
    OCPI 8.4.15. Image class
    '''
    url: HttpUrl = Field(description='URL from where the image data can be fetched through a web browser.')
    thumbnail: HttpUrl | None = Field(None, description='URL from where a thumbnail of the image can be fetched through a webbrowser.')
    category: OcpiImageCategoryEnum = Field(description='Describes what the image is used for.')
    type: str = Field(description='Image type like: gif, jpeg, png, svg.')
    width: int | None = Field(None, description='Width of the full scale image.', gt=0, le=99999)
    height: int | None = Field(None, description='Height of the full scale image.', gt=0, le=99999)

    _example: ClassVar[dict] = {
        'url': 'https://wincharge.com.tw/wp-content/uploads/2022/07/logo_wincharge_banner_blue.png',
        'category': 'OPERATOR',
        'type': 'png',
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiBusinessDetails(BaseModel):
    '''
    OCPI 8.4.2. BusinessDetails class
    '''
    name: str = Field(description='Name of the operator.')
    website: str | None = Field(None, description='Link to the operator’s website.')
    logo: OcpiImage | None = Field(None, description='Image link to the operator’s logo.')

    _example: ClassVar[dict] = {
        'name': 'WinCharge',
        'website': 'https://www.wincharge.com.tw',
        # 'logo': OcpiImage._example,
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiGeoLocation(BaseModel):
    '''
    OCPI 8.4.13. GeoLoation class

    - WGS 84 坐標系。
    '''
    latitude: str = Field(description='Latitude of the point in decimal degree.', max_length=10)
    longitude: str = Field(description='Longitude of the point in decimal degree.', max_length=11)

    _example: ClassVar[dict] = {"latitude": "51.047599", "longitude": "3.729944"}
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})


