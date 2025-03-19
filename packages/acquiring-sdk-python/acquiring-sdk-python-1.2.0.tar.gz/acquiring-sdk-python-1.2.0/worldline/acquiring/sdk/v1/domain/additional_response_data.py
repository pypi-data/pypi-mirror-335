# -*- coding: utf-8 -*-
#
# This file was automatically generated.
#
from typing import Optional

from worldline.acquiring.sdk.domain.data_object import DataObject


class AdditionalResponseData(DataObject):

    __merchant_advice_code: Optional[str] = None
    __merchant_advice_code_description: Optional[str] = None

    @property
    def merchant_advice_code(self) -> Optional[str]:
        """
        | Merchant advice code as returned by the scheme, usually returned upon rejection. Known possible values at the time of writing this documentation are:
        
        * ``01`` - New Account Information Available
        * ``02`` - Try Again Later
        * ``03`` - Do Not Try Again
        * ``04`` - Token requirements not fulfilled for this token type
        * ``05`` - Negotiated value not provided
        * ``21`` - Payment Cancellation
        * ``22`` - Merchant does not qualify for product code
        * ``24`` - Retry after 1 hour
        * ``25`` - Retry after 24 hours
        * ``26`` - Retry after 2 days
        * ``27`` - Retry after 4 days
        * ``28`` - Retry after 6 days
        * ``29`` - Retry after 8 days
        * ``30`` - Retry after 10 days
        * ``40`` - Consumer non-reloadable prepaid card
        * ``41`` - Consumer single-use virtual card number
        * ``42`` - Sanctions Scoring Service: Score Exceeds Applicable Threshold Value
        * ``43`` - Consumer multi-use virtual card number Note: In case new values are added and returned by the schemes, they will be returned as is. We will maintain the above list on a best-effort basis.

        Type: str
        """
        return self.__merchant_advice_code

    @merchant_advice_code.setter
    def merchant_advice_code(self, value: Optional[str]) -> None:
        self.__merchant_advice_code = value

    @property
    def merchant_advice_code_description(self) -> Optional[str]:
        """
        | Human readable description of the merchant advice code. Note: In case the merchant advice code is unknown (unmapped), the system returns ``Unknown``.

        Type: str
        """
        return self.__merchant_advice_code_description

    @merchant_advice_code_description.setter
    def merchant_advice_code_description(self, value: Optional[str]) -> None:
        self.__merchant_advice_code_description = value

    def to_dictionary(self) -> dict:
        dictionary = super(AdditionalResponseData, self).to_dictionary()
        if self.merchant_advice_code is not None:
            dictionary['merchantAdviceCode'] = self.merchant_advice_code
        if self.merchant_advice_code_description is not None:
            dictionary['merchantAdviceCodeDescription'] = self.merchant_advice_code_description
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AdditionalResponseData':
        super(AdditionalResponseData, self).from_dictionary(dictionary)
        if 'merchantAdviceCode' in dictionary:
            self.merchant_advice_code = dictionary['merchantAdviceCode']
        if 'merchantAdviceCodeDescription' in dictionary:
            self.merchant_advice_code_description = dictionary['merchantAdviceCodeDescription']
        return self
