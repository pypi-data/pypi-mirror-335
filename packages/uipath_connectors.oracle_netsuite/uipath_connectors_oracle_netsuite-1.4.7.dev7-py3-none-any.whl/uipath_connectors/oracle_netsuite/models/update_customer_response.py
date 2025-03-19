from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_customer_response_customer_type import (
    UpdateCustomerResponseCustomerType,
)
import datetime
from ..models.update_customer_response_parent import UpdateCustomerResponseParent
from ..models.update_customer_response_alcohol_recipient_type import (
    UpdateCustomerResponseAlcoholRecipientType,
)
from ..models.update_customer_response_subscriptions_list import (
    UpdateCustomerResponseSubscriptionsList,
)
from ..models.update_customer_response_access_role import (
    UpdateCustomerResponseAccessRole,
)
from ..models.update_customer_response_receivables_account import (
    UpdateCustomerResponseReceivablesAccount,
)
from ..models.update_customer_response_email_preference import (
    UpdateCustomerResponseEmailPreference,
)
from ..models.update_customer_response_currency_list import (
    UpdateCustomerResponseCurrencyList,
)
from ..models.update_customer_response_credit_hold_override import (
    UpdateCustomerResponseCreditHoldOverride,
)
from ..models.update_customer_response_global_subscription_status import (
    UpdateCustomerResponseGlobalSubscriptionStatus,
)
from ..models.update_customer_response_language import UpdateCustomerResponseLanguage
from ..models.update_customer_response_currency import UpdateCustomerResponseCurrency
from ..models.update_customer_response_subsidiary import (
    UpdateCustomerResponseSubsidiary,
)
from ..models.update_customer_response_addressbook_list import (
    UpdateCustomerResponseAddressbookList,
)
from ..models.update_customer_response_custom_form import (
    UpdateCustomerResponseCustomForm,
)
from ..models.update_customer_response_stage import UpdateCustomerResponseStage
from ..models.update_customer_response_entity_status import (
    UpdateCustomerResponseEntityStatus,
)
from ..models.update_customer_response_contact_roles_list import (
    UpdateCustomerResponseContactRolesList,
)


class UpdateCustomerResponse(BaseModel):
    """
    Attributes:
        access_role (Optional[UpdateCustomerResponseAccessRole]):
        addressbook_list (Optional[UpdateCustomerResponseAddressbookList]):
        aging (Optional[int]): The Aging Example: 0.0.
        aging1 (Optional[int]): The Aging 1 Example: 0.0.
        aging2 (Optional[int]): The Aging 2 Example: 0.0.
        aging3 (Optional[int]): The Aging 3 Example: 0.0.
        aging4 (Optional[int]): The Aging 4 Example: 0.0.
        alcohol_recipient_type (Optional[UpdateCustomerResponseAlcoholRecipientType]):
        balance (Optional[int]): The Balance Example: 0.0.
        company_name (Optional[str]): The Company name Example: tstCustomerLeustean updated.
        contact_roles_list (Optional[UpdateCustomerResponseContactRolesList]):
        credit_hold_override (Optional[UpdateCustomerResponseCreditHoldOverride]):
        currency (Optional[UpdateCustomerResponseCurrency]):
        currency_list (Optional[UpdateCustomerResponseCurrencyList]):
        custom_form (Optional[UpdateCustomerResponseCustomForm]):
        customer_type (Optional[UpdateCustomerResponseCustomerType]):
        date_created (Optional[datetime.datetime]): The Date created Example: 2024-05-09T11:57:39.0000000+05:30.
        default_address (Optional[str]): The Default address Example: tstCustomerLeustean fdsfsd
                gfgdsfg
                tegf
                vizag Telangana 6365656
                India.
        deposit_balance (Optional[int]): The Deposit balance Example: 0.0.
        email (Optional[str]): The Email Example: bogdan.leustean@yahoo.com.
        email_preference (Optional[UpdateCustomerResponseEmailPreference]):
        email_transactions (Optional[bool]): The Email transactions
        entity_id (Optional[str]): The Entity ID Example: 4582 tstCustomerLeustean fdsfsd.
        entity_status (Optional[UpdateCustomerResponseEntityStatus]):
        fax_transactions (Optional[bool]): The Fax transactions
        first_name (Optional[str]): The First name Example: fakervdsd.
        give_access (Optional[bool]): The Give access
        global_subscription_status (Optional[UpdateCustomerResponseGlobalSubscriptionStatus]):
        internal_id (Optional[str]): Customer ID Example: 730913.
        is_budget_approved (Optional[bool]): The Is budget approved
        is_inactive (Optional[bool]): The Is inactive
        is_person (Optional[bool]): The Is person
        language (Optional[UpdateCustomerResponseLanguage]):
        last_modified_date (Optional[datetime.datetime]): The Last modified date Example:
                2024-05-09T12:17:38.0000000+05:30.
        last_name (Optional[str]): The Last name Example: fakerfdsfdf.
        middle_name (Optional[str]): The Middle name Example: fakerfdsfds.
        overdue_balance (Optional[int]): The Overdue balance Example: 0.0.
        parent (Optional[UpdateCustomerResponseParent]):
        phone (Optional[str]): The Phone Example: +19999.
        print_transactions (Optional[bool]): The Print transactions
        receivables_account (Optional[UpdateCustomerResponseReceivablesAccount]):
        salutation (Optional[str]): The Salutation Example: fakerfdsfsd.
        send_email (Optional[bool]): The Send email
        ship_complete (Optional[bool]): The Ship complete
        stage (Optional[UpdateCustomerResponseStage]):
        subscriptions_list (Optional[UpdateCustomerResponseSubscriptionsList]):
        subsidiary (Optional[UpdateCustomerResponseSubsidiary]):
        sync_partner_teams (Optional[bool]): The Sync partner teams
        tax_exempt (Optional[bool]): The Tax exempt
        taxable (Optional[bool]): The Taxable Example: True.
        unbilled_orders (Optional[int]): The Unbilled orders Example: 0.0.
        url (Optional[str]): The Url Example: https://wwe.com.
        web_lead (Optional[str]): The Web lead Example: No.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    access_role: Optional["UpdateCustomerResponseAccessRole"] = Field(
        alias="accessRole", default=None
    )
    addressbook_list: Optional["UpdateCustomerResponseAddressbookList"] = Field(
        alias="addressbookList", default=None
    )
    aging: Optional[int] = Field(alias="aging", default=None)
    aging1: Optional[int] = Field(alias="aging1", default=None)
    aging2: Optional[int] = Field(alias="aging2", default=None)
    aging3: Optional[int] = Field(alias="aging3", default=None)
    aging4: Optional[int] = Field(alias="aging4", default=None)
    alcohol_recipient_type: Optional["UpdateCustomerResponseAlcoholRecipientType"] = (
        Field(alias="alcoholRecipientType", default=None)
    )
    balance: Optional[int] = Field(alias="balance", default=None)
    company_name: Optional[str] = Field(alias="companyName", default=None)
    contact_roles_list: Optional["UpdateCustomerResponseContactRolesList"] = Field(
        alias="contactRolesList", default=None
    )
    credit_hold_override: Optional["UpdateCustomerResponseCreditHoldOverride"] = Field(
        alias="creditHoldOverride", default=None
    )
    currency: Optional["UpdateCustomerResponseCurrency"] = Field(
        alias="currency", default=None
    )
    currency_list: Optional["UpdateCustomerResponseCurrencyList"] = Field(
        alias="currencyList", default=None
    )
    custom_form: Optional["UpdateCustomerResponseCustomForm"] = Field(
        alias="customForm", default=None
    )
    customer_type: Optional[UpdateCustomerResponseCustomerType] = Field(
        alias="customerType", default=None
    )
    date_created: Optional[datetime.datetime] = Field(alias="dateCreated", default=None)
    default_address: Optional[str] = Field(alias="defaultAddress", default=None)
    deposit_balance: Optional[int] = Field(alias="depositBalance", default=None)
    email: Optional[str] = Field(alias="email", default=None)
    email_preference: Optional["UpdateCustomerResponseEmailPreference"] = Field(
        alias="emailPreference", default=None
    )
    email_transactions: Optional[bool] = Field(alias="emailTransactions", default=None)
    entity_id: Optional[str] = Field(alias="entityId", default=None)
    entity_status: Optional["UpdateCustomerResponseEntityStatus"] = Field(
        alias="entityStatus", default=None
    )
    fax_transactions: Optional[bool] = Field(alias="faxTransactions", default=None)
    first_name: Optional[str] = Field(alias="firstName", default=None)
    give_access: Optional[bool] = Field(alias="giveAccess", default=None)
    global_subscription_status: Optional[
        "UpdateCustomerResponseGlobalSubscriptionStatus"
    ] = Field(alias="globalSubscriptionStatus", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    is_budget_approved: Optional[bool] = Field(alias="isBudgetApproved", default=None)
    is_inactive: Optional[bool] = Field(alias="isInactive", default=None)
    is_person: Optional[bool] = Field(alias="isPerson", default=None)
    language: Optional["UpdateCustomerResponseLanguage"] = Field(
        alias="language", default=None
    )
    last_modified_date: Optional[datetime.datetime] = Field(
        alias="lastModifiedDate", default=None
    )
    last_name: Optional[str] = Field(alias="lastName", default=None)
    middle_name: Optional[str] = Field(alias="middleName", default=None)
    overdue_balance: Optional[int] = Field(alias="overdueBalance", default=None)
    parent: Optional["UpdateCustomerResponseParent"] = Field(
        alias="parent", default=None
    )
    phone: Optional[str] = Field(alias="phone", default=None)
    print_transactions: Optional[bool] = Field(alias="printTransactions", default=None)
    receivables_account: Optional["UpdateCustomerResponseReceivablesAccount"] = Field(
        alias="receivablesAccount", default=None
    )
    salutation: Optional[str] = Field(alias="salutation", default=None)
    send_email: Optional[bool] = Field(alias="sendEmail", default=None)
    ship_complete: Optional[bool] = Field(alias="shipComplete", default=None)
    stage: Optional["UpdateCustomerResponseStage"] = Field(alias="stage", default=None)
    subscriptions_list: Optional["UpdateCustomerResponseSubscriptionsList"] = Field(
        alias="subscriptionsList", default=None
    )
    subsidiary: Optional["UpdateCustomerResponseSubsidiary"] = Field(
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
    def from_dict(cls: Type["UpdateCustomerResponse"], src_dict: Dict[str, Any]):
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
