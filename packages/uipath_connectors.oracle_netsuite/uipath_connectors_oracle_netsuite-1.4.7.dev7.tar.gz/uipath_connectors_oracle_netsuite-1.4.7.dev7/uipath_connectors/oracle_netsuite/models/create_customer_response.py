from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.create_customer_response_subscriptions_list import (
    CreateCustomerResponseSubscriptionsList,
)
from ..models.create_customer_response_credit_hold_override import (
    CreateCustomerResponseCreditHoldOverride,
)
from ..models.create_customer_response_stage import CreateCustomerResponseStage
from ..models.create_customer_response_parent import CreateCustomerResponseParent
from ..models.create_customer_response_contact_roles_list import (
    CreateCustomerResponseContactRolesList,
)
from ..models.create_customer_response_receivables_account import (
    CreateCustomerResponseReceivablesAccount,
)
from ..models.create_customer_response_address_1 import CreateCustomerResponseAddress1
from ..models.create_customer_response_currency import CreateCustomerResponseCurrency
from ..models.create_customer_response_entity_status import (
    CreateCustomerResponseEntityStatus,
)
from ..models.create_customer_response_address_2 import CreateCustomerResponseAddress2
from ..models.create_customer_response_alcohol_recipient_type import (
    CreateCustomerResponseAlcoholRecipientType,
)
from ..models.create_customer_response_subsidiary import (
    CreateCustomerResponseSubsidiary,
)
from ..models.create_customer_response_global_subscription_status import (
    CreateCustomerResponseGlobalSubscriptionStatus,
)
from ..models.create_customer_response_custom_form import (
    CreateCustomerResponseCustomForm,
)
from ..models.create_customer_response_email_preference import (
    CreateCustomerResponseEmailPreference,
)
from ..models.create_customer_response_language import CreateCustomerResponseLanguage
from ..models.create_customer_response_access_role import (
    CreateCustomerResponseAccessRole,
)
from ..models.create_customer_response_currency_list import (
    CreateCustomerResponseCurrencyList,
)


class CreateCustomerResponse(BaseModel):
    """
    Attributes:
        access_role (Optional[CreateCustomerResponseAccessRole]):
        address1 (Optional[CreateCustomerResponseAddress1]):
        address2 (Optional[CreateCustomerResponseAddress2]):
        aging (Optional[int]): The Aging Example: 0.0.
        aging1 (Optional[int]): The Aging 1 Example: 0.0.
        aging2 (Optional[int]): The Aging 2 Example: 0.0.
        aging3 (Optional[int]): The Aging 3 Example: 0.0.
        aging4 (Optional[int]): The Aging 4 Example: 0.0.
        alcohol_recipient_type (Optional[CreateCustomerResponseAlcoholRecipientType]):
        balance (Optional[int]): The Balance Example: 0.0.
        company_name (Optional[str]): The Company name Example: tstCustomerLeustean updated.
        contact_roles_list (Optional[CreateCustomerResponseContactRolesList]):
        credit_hold_override (Optional[CreateCustomerResponseCreditHoldOverride]):
        currency (Optional[CreateCustomerResponseCurrency]):
        currency_list (Optional[CreateCustomerResponseCurrencyList]):
        custom_form (Optional[CreateCustomerResponseCustomForm]):
        date_created (Optional[datetime.datetime]): The Date created Example: 2024-05-09T11:57:39.0000000+05:30.
        deposit_balance (Optional[int]): The Deposit balance Example: 0.0.
        email (Optional[str]): The Email Example: bogdan.leustean@yahoo.com.
        email_preference (Optional[CreateCustomerResponseEmailPreference]):
        email_transactions (Optional[bool]): The Email transactions
        entity_id (Optional[str]): The Entity ID Example: 4582 tstCustomerLeustean fdsfsd.
        entity_status (Optional[CreateCustomerResponseEntityStatus]):
        fax_transactions (Optional[bool]): The Fax transactions
        first_name (Optional[str]): The First name Example: fakervdsd.
        give_access (Optional[bool]): The Give access
        global_subscription_status (Optional[CreateCustomerResponseGlobalSubscriptionStatus]):
        internal_id (Optional[str]): Customer ID Example: 730913.
        is_budget_approved (Optional[bool]): The Is budget approved
        is_inactive (Optional[bool]): The Is inactive
        is_person (Optional[bool]): The Is person
        language (Optional[CreateCustomerResponseLanguage]):
        last_modified_date (Optional[datetime.datetime]): The Last modified date Example:
                2024-05-09T12:17:38.0000000+05:30.
        last_name (Optional[str]): The Last name Example: fakerfdsfdf.
        middle_name (Optional[str]): The Middle name Example: fakerfdsfds.
        overdue_balance (Optional[int]): The Overdue balance Example: 0.0.
        parent (Optional[CreateCustomerResponseParent]):
        phone (Optional[str]): The Phone Example: +19999.
        print_transactions (Optional[bool]): The Print transactions
        receivables_account (Optional[CreateCustomerResponseReceivablesAccount]):
        salutation (Optional[str]): The Salutation Example: fakerfdsfsd.
        send_email (Optional[bool]): The Send email
        ship_complete (Optional[bool]): The Ship complete
        stage (Optional[CreateCustomerResponseStage]):
        subscriptions_list (Optional[CreateCustomerResponseSubscriptionsList]):
        subsidiary (Optional[CreateCustomerResponseSubsidiary]):
        sync_partner_teams (Optional[bool]): The Sync partner teams
        tax_exempt (Optional[bool]): The Tax exempt
        taxable (Optional[bool]): The Taxable Example: True.
        unbilled_orders (Optional[int]): The Unbilled orders Example: 0.0.
        url (Optional[str]): The Url Example: https://wwe.com.
        web_lead (Optional[str]): The Web lead Example: No.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    access_role: Optional["CreateCustomerResponseAccessRole"] = Field(
        alias="accessRole", default=None
    )
    address1: Optional["CreateCustomerResponseAddress1"] = Field(
        alias="address1", default=None
    )
    address2: Optional["CreateCustomerResponseAddress2"] = Field(
        alias="address2", default=None
    )
    aging: Optional[int] = Field(alias="aging", default=None)
    aging1: Optional[int] = Field(alias="aging1", default=None)
    aging2: Optional[int] = Field(alias="aging2", default=None)
    aging3: Optional[int] = Field(alias="aging3", default=None)
    aging4: Optional[int] = Field(alias="aging4", default=None)
    alcohol_recipient_type: Optional["CreateCustomerResponseAlcoholRecipientType"] = (
        Field(alias="alcoholRecipientType", default=None)
    )
    balance: Optional[int] = Field(alias="balance", default=None)
    company_name: Optional[str] = Field(alias="companyName", default=None)
    contact_roles_list: Optional["CreateCustomerResponseContactRolesList"] = Field(
        alias="contactRolesList", default=None
    )
    credit_hold_override: Optional["CreateCustomerResponseCreditHoldOverride"] = Field(
        alias="creditHoldOverride", default=None
    )
    currency: Optional["CreateCustomerResponseCurrency"] = Field(
        alias="currency", default=None
    )
    currency_list: Optional["CreateCustomerResponseCurrencyList"] = Field(
        alias="currencyList", default=None
    )
    custom_form: Optional["CreateCustomerResponseCustomForm"] = Field(
        alias="customForm", default=None
    )
    date_created: Optional[datetime.datetime] = Field(alias="dateCreated", default=None)
    deposit_balance: Optional[int] = Field(alias="depositBalance", default=None)
    email: Optional[str] = Field(alias="email", default=None)
    email_preference: Optional["CreateCustomerResponseEmailPreference"] = Field(
        alias="emailPreference", default=None
    )
    email_transactions: Optional[bool] = Field(alias="emailTransactions", default=None)
    entity_id: Optional[str] = Field(alias="entityId", default=None)
    entity_status: Optional["CreateCustomerResponseEntityStatus"] = Field(
        alias="entityStatus", default=None
    )
    fax_transactions: Optional[bool] = Field(alias="faxTransactions", default=None)
    first_name: Optional[str] = Field(alias="firstName", default=None)
    give_access: Optional[bool] = Field(alias="giveAccess", default=None)
    global_subscription_status: Optional[
        "CreateCustomerResponseGlobalSubscriptionStatus"
    ] = Field(alias="globalSubscriptionStatus", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    is_budget_approved: Optional[bool] = Field(alias="isBudgetApproved", default=None)
    is_inactive: Optional[bool] = Field(alias="isInactive", default=None)
    is_person: Optional[bool] = Field(alias="isPerson", default=None)
    language: Optional["CreateCustomerResponseLanguage"] = Field(
        alias="language", default=None
    )
    last_modified_date: Optional[datetime.datetime] = Field(
        alias="lastModifiedDate", default=None
    )
    last_name: Optional[str] = Field(alias="lastName", default=None)
    middle_name: Optional[str] = Field(alias="middleName", default=None)
    overdue_balance: Optional[int] = Field(alias="overdueBalance", default=None)
    parent: Optional["CreateCustomerResponseParent"] = Field(
        alias="parent", default=None
    )
    phone: Optional[str] = Field(alias="phone", default=None)
    print_transactions: Optional[bool] = Field(alias="printTransactions", default=None)
    receivables_account: Optional["CreateCustomerResponseReceivablesAccount"] = Field(
        alias="receivablesAccount", default=None
    )
    salutation: Optional[str] = Field(alias="salutation", default=None)
    send_email: Optional[bool] = Field(alias="sendEmail", default=None)
    ship_complete: Optional[bool] = Field(alias="shipComplete", default=None)
    stage: Optional["CreateCustomerResponseStage"] = Field(alias="stage", default=None)
    subscriptions_list: Optional["CreateCustomerResponseSubscriptionsList"] = Field(
        alias="subscriptionsList", default=None
    )
    subsidiary: Optional["CreateCustomerResponseSubsidiary"] = Field(
        alias="subsidiary", default=None
    )
    sync_partner_teams: Optional[bool] = Field(alias="syncPartnerTeams", default=None)
    tax_exempt: Optional[bool] = Field(alias="taxExempt", default=None)
    taxable: Optional[bool] = Field(alias="taxable", default=None)
    unbilled_orders: Optional[int] = Field(alias="unbilledOrders", default=None)
    url: Optional[str] = Field(alias="url", default=None)
    web_lead: Optional[str] = Field(alias="webLead", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateCustomerResponse"], src_dict: Dict[str, Any]):
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
