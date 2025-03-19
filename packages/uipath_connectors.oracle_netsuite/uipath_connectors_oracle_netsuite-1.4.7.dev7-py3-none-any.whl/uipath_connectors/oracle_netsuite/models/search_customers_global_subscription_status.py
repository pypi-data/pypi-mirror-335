from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_customers_global_subscription_status_global_subscription_status_value import (
    SearchCustomersGlobalSubscriptionStatusGlobalSubscriptionStatusValue,
)


class SearchCustomersGlobalSubscriptionStatus(BaseModel):
    """
    Attributes:
        value (Optional[SearchCustomersGlobalSubscriptionStatusGlobalSubscriptionStatusValue]): Email recipients can
                have one of four subscription statuses:    * Confirmed Opt-In - When an email recipient has indicated that they
                want to receive your campaign and bulk merge email, they are assigned this subscription status. Only a recipient
                can set his or her subscription status to Confirmed Opt-In.    * Soft Opt-In - Recipients with this status can
                receive opt-in messages that enable them to confirm whether or not they want to receive your email campaigns as
                well as bulk email.      You can set a recipient’s status to Soft Opt-In manually or through a mass update.    *
                Soft Opt-Out - Recipients with this status cannot receive campaign or bulk email messages but can receive opt-in
                messages.      You can change this subscription status to Soft Opt-In manually or through a mass update.    *
                Confirmed Opt-Out - Only the recipient can set their subscription status to Confirmed Opt-Out.      Recipients
                with this status cannot receive email campaigns, bulk email, or opt-in messages. Recipients with this status can
                only opt in again through the Customer Center or by clicking the link in an email message they have received
                prior to opting out.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[
        SearchCustomersGlobalSubscriptionStatusGlobalSubscriptionStatusValue
    ] = Field(alias="value", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchCustomersGlobalSubscriptionStatus"], src_dict: Dict[str, Any]
    ):
        return cls.model_validate(src_dict)

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__
