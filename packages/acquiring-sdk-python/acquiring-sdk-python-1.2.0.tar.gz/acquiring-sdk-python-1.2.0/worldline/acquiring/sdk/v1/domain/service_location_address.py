# -*- coding: utf-8 -*-
#
# This file was automatically generated.
#
from typing import Optional

from worldline.acquiring.sdk.domain.data_object import DataObject


class ServiceLocationAddress(DataObject):

    __city: Optional[str] = None
    __country_code: Optional[str] = None
    __country_subdivision_code: Optional[str] = None
    __postal_code: Optional[str] = None

    @property
    def city(self) -> Optional[str]:
        """
        | Address city

        Type: str
        """
        return self.__city

    @city.setter
    def city(self, value: Optional[str]) -> None:
        self.__city = value

    @property
    def country_code(self) -> Optional[str]:
        """
        | Address country code, ISO 3166 international standard

        Type: str
        """
        return self.__country_code

    @country_code.setter
    def country_code(self, value: Optional[str]) -> None:
        self.__country_code = value

    @property
    def country_subdivision_code(self) -> Optional[str]:
        """
        | Address country subdivision code, see `list <https://docs.acquiring.worldline-solutions.com/Features/References/country-subdivision-codes>`_ for details

        Type: str
        """
        return self.__country_subdivision_code

    @country_subdivision_code.setter
    def country_subdivision_code(self, value: Optional[str]) -> None:
        self.__country_subdivision_code = value

    @property
    def postal_code(self) -> Optional[str]:
        """
        | Address postal code

        Type: str
        """
        return self.__postal_code

    @postal_code.setter
    def postal_code(self, value: Optional[str]) -> None:
        self.__postal_code = value

    def to_dictionary(self) -> dict:
        dictionary = super(ServiceLocationAddress, self).to_dictionary()
        if self.city is not None:
            dictionary['city'] = self.city
        if self.country_code is not None:
            dictionary['countryCode'] = self.country_code
        if self.country_subdivision_code is not None:
            dictionary['countrySubdivisionCode'] = self.country_subdivision_code
        if self.postal_code is not None:
            dictionary['postalCode'] = self.postal_code
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ServiceLocationAddress':
        super(ServiceLocationAddress, self).from_dictionary(dictionary)
        if 'city' in dictionary:
            self.city = dictionary['city']
        if 'countryCode' in dictionary:
            self.country_code = dictionary['countryCode']
        if 'countrySubdivisionCode' in dictionary:
            self.country_subdivision_code = dictionary['countrySubdivisionCode']
        if 'postalCode' in dictionary:
            self.postal_code = dictionary['postalCode']
        return self
