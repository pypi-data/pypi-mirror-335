# -*- coding: utf-8 -*-
#
# This file was automatically generated.
#
from typing import Optional

from worldline.acquiring.sdk.domain.data_object import DataObject


class GeoCoordinates(DataObject):

    __latitude: Optional[float] = None
    __longitude: Optional[float] = None

    @property
    def latitude(self) -> Optional[float]:
        """
        | Latitude of the service location

        Type: float
        """
        return self.__latitude

    @latitude.setter
    def latitude(self, value: Optional[float]) -> None:
        self.__latitude = value

    @property
    def longitude(self) -> Optional[float]:
        """
        | Longitude of the service location

        Type: float
        """
        return self.__longitude

    @longitude.setter
    def longitude(self, value: Optional[float]) -> None:
        self.__longitude = value

    def to_dictionary(self) -> dict:
        dictionary = super(GeoCoordinates, self).to_dictionary()
        if self.latitude is not None:
            dictionary['latitude'] = self.latitude
        if self.longitude is not None:
            dictionary['longitude'] = self.longitude
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'GeoCoordinates':
        super(GeoCoordinates, self).from_dictionary(dictionary)
        if 'latitude' in dictionary:
            self.latitude = dictionary['latitude']
        if 'longitude' in dictionary:
            self.longitude = dictionary['longitude']
        return self
