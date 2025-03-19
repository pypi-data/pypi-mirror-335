# -*- coding: utf-8 -*-
#
# This file was automatically generated.
#
from typing import Optional

from .geo_coordinates import GeoCoordinates
from .service_location_address import ServiceLocationAddress

from worldline.acquiring.sdk.domain.data_object import DataObject


class ServiceLocationData(DataObject):

    __address: Optional[ServiceLocationAddress] = None
    __geo_coordinates: Optional[GeoCoordinates] = None

    @property
    def address(self) -> Optional[ServiceLocationAddress]:
        """
        | Address where the cardholder received the service

        Type: :class:`worldline.acquiring.sdk.v1.domain.service_location_address.ServiceLocationAddress`
        """
        return self.__address

    @address.setter
    def address(self, value: Optional[ServiceLocationAddress]) -> None:
        self.__address = value

    @property
    def geo_coordinates(self) -> Optional[GeoCoordinates]:
        """
        | Geographical coordinates where the cardholder received the service. Geographical coordinates in decimal degree (DD) format Latitude,Longitude where Latitude and Longitude are floating point numbers with the unit degree. Integer and decimal digits are separated by a dot. East and north are indicated by positive numbers whereas west and south have negative ones.

        Type: :class:`worldline.acquiring.sdk.v1.domain.geo_coordinates.GeoCoordinates`
        """
        return self.__geo_coordinates

    @geo_coordinates.setter
    def geo_coordinates(self, value: Optional[GeoCoordinates]) -> None:
        self.__geo_coordinates = value

    def to_dictionary(self) -> dict:
        dictionary = super(ServiceLocationData, self).to_dictionary()
        if self.address is not None:
            dictionary['address'] = self.address.to_dictionary()
        if self.geo_coordinates is not None:
            dictionary['geoCoordinates'] = self.geo_coordinates.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ServiceLocationData':
        super(ServiceLocationData, self).from_dictionary(dictionary)
        if 'address' in dictionary:
            if not isinstance(dictionary['address'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['address']))
            value = ServiceLocationAddress()
            self.address = value.from_dictionary(dictionary['address'])
        if 'geoCoordinates' in dictionary:
            if not isinstance(dictionary['geoCoordinates'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['geoCoordinates']))
            value = GeoCoordinates()
            self.geo_coordinates = value.from_dictionary(dictionary['geoCoordinates'])
        return self
