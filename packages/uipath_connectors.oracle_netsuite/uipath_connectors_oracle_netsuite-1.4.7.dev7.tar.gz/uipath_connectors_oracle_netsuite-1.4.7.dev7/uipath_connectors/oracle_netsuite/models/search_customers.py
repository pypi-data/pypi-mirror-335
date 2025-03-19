from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.search_customers_credit_hold_override import (
    SearchCustomersCreditHoldOverride,
)
from ..models.search_customers_null_field_list import SearchCustomersNullFieldList
from ..models.search_customers_email_preference import SearchCustomersEmailPreference
from ..models.search_customers_sales_team_list import SearchCustomersSalesTeamList
from ..models.search_customers_stage import SearchCustomersStage
from ..models.search_customers_monthly_closing import SearchCustomersMonthlyClosing
from ..models.search_customers_credit_cards_list import SearchCustomersCreditCardsList
from ..models.search_customers_contact_roles_list import SearchCustomersContactRolesList
from ..models.search_customers_group_pricing_list import SearchCustomersGroupPricingList
from ..models.search_customers_symbol_placement import SearchCustomersSymbolPlacement
from ..models.search_customers_tax_registration_list import (
    SearchCustomersTaxRegistrationList,
)
from ..models.search_customers_download_list import SearchCustomersDownloadList
from ..models.search_customers_global_subscription_status import (
    SearchCustomersGlobalSubscriptionStatus,
)
from ..models.search_customers_custom_field_list import SearchCustomersCustomFieldList
from ..models.search_customers_negative_number_format import (
    SearchCustomersNegativeNumberFormat,
)
from ..models.search_customers_record_ref import SearchCustomersRecordRef
from ..models.search_customers_language import SearchCustomersLanguage
from ..models.search_customers_item_pricing_list import SearchCustomersItemPricingList
from ..models.search_customers_alcohol_recipient_type import (
    SearchCustomersAlcoholRecipientType,
)
from ..models.search_customers_addressbook_list import SearchCustomersAddressbookList
from ..models.search_customers_partners_list import SearchCustomersPartnersList
from ..models.search_customers_currency_list import SearchCustomersCurrencyList
from ..models.search_customers_third_party_country import (
    SearchCustomersThirdPartyCountry,
)
from ..models.search_customers_number_format import SearchCustomersNumberFormat
from ..models.search_customers_subscriptions_list import (
    SearchCustomersSubscriptionsList,
)


class SearchCustomers(BaseModel):
    """
    Attributes:
        access_role (Optional[SearchCustomersRecordRef]):
        account_number (Optional[str]): Assigned account number for this customer. Required when ...
        addressbook_list (Optional[SearchCustomersAddressbookList]):
        aging (Optional[float]): The overdue A/R balance is shown here with the balance totals for each aging period.
        aging1 (Optional[float]): The overdue A/R balance is shown here.
        aging2 (Optional[float]): The overdue A/R balance is shown here.
        aging3 (Optional[float]): The overdue A/R balance is shown here.
        aging4 (Optional[float]): The overdue A/R balance is shown here.
        alcohol_recipient_type (Optional[SearchCustomersAlcoholRecipientType]):
        alt_email (Optional[str]): Enter an alternative email address for this person.
        alt_name (Optional[str]): This is the name of this person or company.
        alt_phone (Optional[str]): Phone numbers can be entered in the following formats: 99...
        assigned_web_site (Optional[SearchCustomersRecordRef]):
        balance (Optional[float]): Customer's current accounts receivable balance. This field is returned in an advanced
                search only. It is not returned when using the CustomerSearchBasic search object. Note that in your advanced
                search you must set the BodyFieldsOnly flag to false. This field is a read-only field.NetSuite converts the
                balance of all transactions in foreign currencies to your preferred currency using the exchange rate for the
                current date.
        bill_pay (Optional[bool]): When enabled, the companyName, phone, accountNumber field...
        buying_reason (Optional[SearchCustomersRecordRef]):
        buying_time_frame (Optional[SearchCustomersRecordRef]):
        campaign_category (Optional[SearchCustomersRecordRef]):
        category (Optional[SearchCustomersRecordRef]):
        click_stream (Optional[str]): Read-only field that returns the click stream for this customer on first visit.
        comments (Optional[str]): Enter any other information you wish to track for this customer.
        company_name (Optional[str]): The name of the customer. Required when billPay is enable...
        consol_aging (Optional[float]): The overdue consolidated A/R balance is shown here with the balance totals for
                each aging period. These totals include the balance from all the customers and subcustomers in this hierarchy.
        consol_aging_1 (Optional[float]): The overdue consolidated A/R balance is shown here with the balance totals for
                each aging period. These totals include the balance from all the customers and subcustomers in this hierarchy.
        consol_aging_2 (Optional[float]): The overdue consolidated A/R balance is shown here with the balance totals for
                each aging period. These totals include the balance from all the customers and subcustomers in this hierarchy.
        consol_aging_3 (Optional[float]): The overdue consolidated A/R balance is shown here with the balance totals for
                each aging period. These totals include the balance from all the customers and subcustomers in this hierarchy.
        consol_aging_4 (Optional[float]): The overdue consolidated A/R balance is shown here with the balance totals for
                each aging period. These totals include the balance from all the customers and subcustomers in this hierarchy.
        consol_balance (Optional[float]): The current accounts receivable balance due for the customer-subcustomer
                hierarchy this customer is a part of is shown here.
        consol_days_overdue (Optional[int]): This field shows the number of days overdue the consolidated overdue
                balance is.
        consol_deposit_balance (Optional[float]): This field displays the total amount of unapplied deposits for the
                customer-subcustomer hierarchy this customer is a member of.Deposits are recorded in the general ledger, as a
                liability, when the customer makes an advance payment before delivery of goods or services. A deposit balance
                exists until the goods or services are delivered. Deposits do not affect the customer's accounts receivable
                balance.
        consol_overdue_balance (Optional[float]): This field shows the consolidated total owed for open transactions for
                this customer-subcustomer hierarchy that are past their due date based on the invoice terms.Note: For open
                transactions that do not have a due date, the transaction date is used as the due date to calculate this total.
        consol_unbilled_orders (Optional[float]): This field displays the total amount of orders that have been entered
                but not yet billed for the customer-subcustomer hierarchy this customer is a part of. If you have enabled the
                preference Customer Credit Limit Includes Orders, then this total is included in credit limit calculations. Set
                this preference at <_TABNAME=ADMI_ACCTSETUP_> > <_TASKCATEGORY=ADMI_ACCTSETUP_> > Set Up Accounting > General.
        contact_roles_list (Optional[SearchCustomersContactRolesList]):
        contrib_pct (Optional[str]):
        credit_cards_list (Optional[SearchCustomersCreditCardsList]):
        credit_hold_override (Optional[SearchCustomersCreditHoldOverride]):
        credit_limit (Optional[float]): A credit limit for this customer. If set, and depending on preferences, a
                warning is generated when this customer's limit is exceeded during a transaction addition.
        currency (Optional[SearchCustomersRecordRef]):
        currency_list (Optional[SearchCustomersCurrencyList]):
        custom_field_list (Optional[SearchCustomersCustomFieldList]):
        custom_form (Optional[SearchCustomersRecordRef]):
        date_created (Optional[datetime.datetime]): When adding a record, this field defaults to the current system date
                and time. This field cannot be overwritten. Note: In search, this field respects search criteria down to the
                second.
        days_overdue (Optional[int]): The number of days overdue this balance is overdue is shown here.
        default_address (Optional[str]): Read-only field that returns the default Billing address ...
        default_order_priority (Optional[float]): Enter a number to designate the priority for this customer.
        default_tax_reg (Optional[SearchCustomersRecordRef]):
        deposit_balance (Optional[float]): This field is returned in an advanced search only. It is not returned when
                using the CustomerSearchBasic search object. Note that in your advanced search you must set the BodyFieldsOnly
                flag to false. This field is a read-only field
        display_symbol (Optional[str]): Enter a currency symbol and text to use for this currency.  Include spaces if
                you want to separate the symbol from the currency value.For example, $ USD or $CAD.Use the Symbol Placement
                field to select where the symbol appears.
        download_list (Optional[SearchCustomersDownloadList]):
        dr_account (Optional[SearchCustomersRecordRef]):
        email (Optional[str]): Sets the email address for the customer. If giveAccess is...
        email_preference (Optional[SearchCustomersEmailPreference]):
        email_transactions (Optional[bool]): Set a preferred transaction delivery method for this customer. Choose to
                send transactions by regular mail, by email, by fax, or by a combination of the three. Then, when you select the
                customer on a transaction, their preferred delivery method is marked by default.    * Email – Check this box to
                check the To Be Emailed box by default on transactions when this customer is selected.    * Print – Check this
                box to check the To Be Printed box by default on transactions when this customer is selected.    * Fax – Check
                this box to check the To Be Faxed box by default on transactions when this customer is selected.Once you enter
                these settings on the customer record, these boxes are checked by default for transactions created from the
                customer record or for transactions that are copied or converted.Note: These settings override any customized
                settings on transaction forms you use.There are also preferences to set default values for new customer records
                at Setup > Company > Preferences > Printing, Fax,&amp; Email Preferences. On the Print subtab, Fax subtab, or
                Email subtab, check Customers Default to [Print/Fax/Email] Transactions.You can also set these fields using the
                Mass Update function. Go to Lists > Mass Updates > Mass Updates > General and click Customer.
        end_date (Optional[datetime.datetime]): Projected end date for this customer (used in the case of...
        entity_id (Optional[str]): The name of the customer record. Required on add and upda...
        entity_status (Optional[SearchCustomersRecordRef]):
        estimated_budget (Optional[float]): Enter the estimated budget the prospect or customer has for this
                opportunity.
        external_id (Optional[str]): External Id
        fax (Optional[str]): Sets the fax number for the customer.
        fax_transactions (Optional[bool]): Set a preferred transaction delivery method for this customer. Choose to send
                transactions by regular mail, by email, by fax, or by a combination of the three. Then, when you select the
                customer on a transaction, their preferred delivery method is marked by default.    * Email – Check this box to
                check the To Be Emailed box by default on transactions when this customer is selected.    * Print – Check this
                box to check the To Be Printed box by default on transactions when this customer is selected.    * Fax – Check
                this box to check the To Be Faxed box by default on transactions when this customer is selected.Once you enter
                these settings on the customer record, these boxes are checked by default for transactions created from the
                customer record or for transactions that are copied or converted.Note: These settings override any customized
                settings on transaction forms you use.There are also preferences to set default values for new customer records
                at Setup > Company > Preferences > Printing, Fax,&amp; Email Preferences. On the Print subtab, Fax subtab, or
                Email subtab, check Customers Default to [Print/Fax/Email] Transactions.You can also set these fields using the
                Mass Update function. Go to Lists > Mass Updates > Mass Updates > General and click Customer.
        first_name (Optional[str]): Required when the isPerson field is set as TRUE designati...
        first_visit (Optional[datetime.datetime]): Read-only field that returns the date the customer first ...
        fx_account (Optional[SearchCustomersRecordRef]):
        give_access (Optional[bool]): Enables access to your NetSuite account for the customer.
        global_subscription_status (Optional[SearchCustomersGlobalSubscriptionStatus]):
        group_pricing_list (Optional[SearchCustomersGroupPricingList]):
        home_phone (Optional[str]): Only settable when isPerson is set to TRUE defining this ...
        image (Optional[SearchCustomersRecordRef]):
        internal_id (Optional[str]): Internal Id which serves as primary key
        is_budget_approved (Optional[bool]): Check this box if the customer's budget has been approved.
        is_inactive (Optional[bool]): This field is false by default.
        is_person (Optional[bool]): By default, this is set to True which specifies the type ...
        item_pricing_list (Optional[SearchCustomersItemPricingList]):
        keywords (Optional[str]): This is a read-only field that returns the search engine ...
        language (Optional[SearchCustomersLanguage]):
        last_modified_date (Optional[datetime.datetime]):
        last_name (Optional[str]): Required when the isPerson field is set as TRUE designating this customer as an
                Individual.
        last_page_visited (Optional[str]): This field displays the last page this customer viewed on his or her most
                recent visit to your Web site.
        last_visit (Optional[datetime.datetime]): Read-only field that returns the date the customer first visited the
                account website.
        lead_source (Optional[SearchCustomersRecordRef]):
        middle_name (Optional[str]):
        mobile_phone (Optional[str]): Only settable when isPerson is set to TRUE defining this customer as an
                individual.
        monthly_closing (Optional[SearchCustomersMonthlyClosing]):
        negative_number_format (Optional[SearchCustomersNegativeNumberFormat]):
        null_field_list (Optional[SearchCustomersNullFieldList]):
        number_format (Optional[SearchCustomersNumberFormat]):
        opening_balance (Optional[float]): Enter the opening balance of this customer's account.
        opening_balance_account (Optional[SearchCustomersRecordRef]):
        opening_balance_date (Optional[datetime.datetime]): Enter the date of the balance entered in the Opening Balance
                field.
        overdue_balance (Optional[float]): This field is returned in an advanced search only. It is not returned when
                using the CustomerSearchBasic search object. Note that in your advanced search you must set the BodyFieldsOnly
                flag to false. This field is a read-only field.NetSuite converts the overdue balance of all transactions in
                foreign currencies to your preferred currency using the exchange rate for the current date.
        override_currency_format (Optional[bool]): Check this box to customize the currency format.
        parent (Optional[SearchCustomersRecordRef]):
        partner (Optional[SearchCustomersRecordRef]):
        partners_list (Optional[SearchCustomersPartnersList]):
        password (Optional[str]): Sets the password assigned to allow this customer access to NetSuite.
        password2 (Optional[str]): Sets the password confirmation field.
        phone (Optional[str]): Enter a phone number for your customer. It will appear on the Customer List report.
        phonetic_name (Optional[str]): Enter the furigana character you want to use to sort this record.
        pref_cc_processor (Optional[SearchCustomersRecordRef]):
        price_level (Optional[SearchCustomersRecordRef]):
        print_on_check_as (Optional[str]): What you enter here prints on the Pay to the Order of line of a check instead
                of what you entered in the Customer field.
        print_transactions (Optional[bool]): Set a preferred transaction delivery method for this customer. Choose to
                send transactions by regular mail, by email, by fax, or by a combination of the three. Then, when you select the
                customer on a transaction, their preferred delivery method is marked by default.    * Email – Check this box to
                check the To Be Emailed box by default on transactions when this customer is selected.    * Print – Check this
                box to check the To Be Printed box by default on transactions when this customer is selected.    * Fax – Check
                this box to check the To Be Faxed box by default on transactions when this customer is selected.Once you enter
                these settings on the customer record, these boxes are checked by default for transactions created from the
                customer record or for transactions that are copied or converted.Note: These settings override any customized
                settings on transaction forms you use.There are also preferences to set default values for new customer records
                at Setup > Company > Preferences > Printing, Fax,&amp; Email Preferences. On the Print subtab, Fax subtab, or
                Email subtab, check Customers Default to [Print/Fax/Email] Transactions.You can also set these fields using the
                Mass Update function. Go to Lists > Mass Updates > Mass Updates > General and click Customer.
        receivables_account (Optional[SearchCustomersRecordRef]):
        referrer (Optional[str]): Read-only field that returns the site that referred the customer to the NetSuite
                account website.
        reminder_days (Optional[int]): Sets the number of days before the end date that a reminder should be sent for
                renewing a customer's contract or project.
        representing_subsidiary (Optional[SearchCustomersRecordRef]):
        require_pwd_change (Optional[bool]):
        resale_number (Optional[str]): Customer's  tax license number for cases where you do not collect sales tax from
                this customer because the merchandise will be resold.
        sales_group (Optional[SearchCustomersRecordRef]):
        sales_readiness (Optional[SearchCustomersRecordRef]):
        sales_rep (Optional[SearchCustomersRecordRef]):
        sales_team_list (Optional[SearchCustomersSalesTeamList]):
        salutation (Optional[str]): Enter the title of this person, such as Mr., Mrs., Ms., Dr., Rev., etc.
        send_email (Optional[bool]): If true, the customer is automatically sent an email notification when access to
                NetSuite is provided.
        ship_complete (Optional[bool]): Check this box if you only want to ship orders to this customer when they are
                completely fulfilled.
        shipping_item (Optional[SearchCustomersRecordRef]):
        source_web_site (Optional[SearchCustomersRecordRef]):
        stage (Optional[SearchCustomersStage]):
        start_date (Optional[datetime.datetime]): Enter the date this person or company became a customer, lead or
                prospect.If this person or company has a contract with you, enter the start date of the contract.If you enter an
                estimate or an opportunity for this customer, this field will be updated with the date of that transaction.
        subscriptions_list (Optional[SearchCustomersSubscriptionsList]):
        subsidiary (Optional[SearchCustomersRecordRef]):
        symbol_placement (Optional[SearchCustomersSymbolPlacement]):
        sync_partner_teams (Optional[bool]): Check this box if you want to update this customer's transactions to
                reflect the changes you make to the partner team.
        tax_exempt (Optional[bool]):
        tax_item (Optional[SearchCustomersRecordRef]):
        tax_registration_list (Optional[SearchCustomersTaxRegistrationList]):
        taxable (Optional[bool]): True indicates that this customer pays sales tax according to the rate defined in the
                tax Item field. False indicates that this customer does not pay sales tax, but only if Tax Item field is empty.
        terms (Optional[SearchCustomersRecordRef]):
        territory (Optional[SearchCustomersRecordRef]):
        third_party_acct (Optional[str]): Enter this customer’s FedEx® or UPS® account number in the 3rd Party Billing
                Account Number field.This account number is used if you select Consignee Billing on item fulfillments using UPS
                or select Bill Recipient on item fulfillments using FedEx.
        third_party_country (Optional[SearchCustomersThirdPartyCountry]):
        third_party_zipcode (Optional[str]): Enter the zip code associated with the customer’s UPS or FedEx account
                number.
        title (Optional[str]): Enter the job title for this person's position at his or her company.
        unbilled_orders (Optional[float]): This field displays the total amount of orders that have been entered but not
                yet billed.If you have enabled the preference Customer Credit Limit Includes Orders, then this total is included
                in credit limit calculations.Set this preference at <_TABNAME=ADMI_ACCTSETUP_> > <_TASKCATEGORY=ADMI_ACCTSETUP_>
                > Set Up Accounting > General.If you use the Multiple Currencies feature, the amount in this field is shown in
                the customer's currency.
        url (Optional[str]): Sets the URL associated with the customer.
        vat_reg_number (Optional[str]): For the UK edition only. Note that this field is not validated when submitted
                via Web services.
        visits (Optional[int]): This field displays the total number of visits this customer has made to your Web site.A
                new visit is counted after the customer leaves your site and returns.
        web_lead (Optional[str]): This is a read-only hidden field that defines whether a customer registered via a
                NetSuite website. It returns a string of either Yes or No.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    access_role: Optional["SearchCustomersRecordRef"] = Field(
        alias="accessRole", default=None
    )
    account_number: Optional[str] = Field(alias="accountNumber", default=None)
    addressbook_list: Optional["SearchCustomersAddressbookList"] = Field(
        alias="addressbookList", default=None
    )
    aging: Optional[float] = Field(alias="aging", default=None)
    aging1: Optional[float] = Field(alias="aging1", default=None)
    aging2: Optional[float] = Field(alias="aging2", default=None)
    aging3: Optional[float] = Field(alias="aging3", default=None)
    aging4: Optional[float] = Field(alias="aging4", default=None)
    alcohol_recipient_type: Optional["SearchCustomersAlcoholRecipientType"] = Field(
        alias="alcoholRecipientType", default=None
    )
    alt_email: Optional[str] = Field(alias="altEmail", default=None)
    alt_name: Optional[str] = Field(alias="altName", default=None)
    alt_phone: Optional[str] = Field(alias="altPhone", default=None)
    assigned_web_site: Optional["SearchCustomersRecordRef"] = Field(
        alias="assignedWebSite", default=None
    )
    balance: Optional[float] = Field(alias="balance", default=None)
    bill_pay: Optional[bool] = Field(alias="billPay", default=None)
    buying_reason: Optional["SearchCustomersRecordRef"] = Field(
        alias="buyingReason", default=None
    )
    buying_time_frame: Optional["SearchCustomersRecordRef"] = Field(
        alias="buyingTimeFrame", default=None
    )
    campaign_category: Optional["SearchCustomersRecordRef"] = Field(
        alias="campaignCategory", default=None
    )
    category: Optional["SearchCustomersRecordRef"] = Field(
        alias="category", default=None
    )
    click_stream: Optional[str] = Field(alias="clickStream", default=None)
    comments: Optional[str] = Field(alias="comments", default=None)
    company_name: Optional[str] = Field(alias="companyName", default=None)
    consol_aging: Optional[float] = Field(alias="consolAging", default=None)
    consol_aging_1: Optional[float] = Field(alias="consolAging1", default=None)
    consol_aging_2: Optional[float] = Field(alias="consolAging2", default=None)
    consol_aging_3: Optional[float] = Field(alias="consolAging3", default=None)
    consol_aging_4: Optional[float] = Field(alias="consolAging4", default=None)
    consol_balance: Optional[float] = Field(alias="consolBalance", default=None)
    consol_days_overdue: Optional[int] = Field(alias="consolDaysOverdue", default=None)
    consol_deposit_balance: Optional[float] = Field(
        alias="consolDepositBalance", default=None
    )
    consol_overdue_balance: Optional[float] = Field(
        alias="consolOverdueBalance", default=None
    )
    consol_unbilled_orders: Optional[float] = Field(
        alias="consolUnbilledOrders", default=None
    )
    contact_roles_list: Optional["SearchCustomersContactRolesList"] = Field(
        alias="contactRolesList", default=None
    )
    contrib_pct: Optional[str] = Field(alias="contribPct", default=None)
    credit_cards_list: Optional["SearchCustomersCreditCardsList"] = Field(
        alias="creditCardsList", default=None
    )
    credit_hold_override: Optional["SearchCustomersCreditHoldOverride"] = Field(
        alias="creditHoldOverride", default=None
    )
    credit_limit: Optional[float] = Field(alias="creditLimit", default=None)
    currency: Optional["SearchCustomersRecordRef"] = Field(
        alias="currency", default=None
    )
    currency_list: Optional["SearchCustomersCurrencyList"] = Field(
        alias="currencyList", default=None
    )
    custom_field_list: Optional["SearchCustomersCustomFieldList"] = Field(
        alias="customFieldList", default=None
    )
    custom_form: Optional["SearchCustomersRecordRef"] = Field(
        alias="customForm", default=None
    )
    date_created: Optional[datetime.datetime] = Field(alias="dateCreated", default=None)
    days_overdue: Optional[int] = Field(alias="daysOverdue", default=None)
    default_address: Optional[str] = Field(alias="defaultAddress", default=None)
    default_order_priority: Optional[float] = Field(
        alias="defaultOrderPriority", default=None
    )
    default_tax_reg: Optional["SearchCustomersRecordRef"] = Field(
        alias="defaultTaxReg", default=None
    )
    deposit_balance: Optional[float] = Field(alias="depositBalance", default=None)
    display_symbol: Optional[str] = Field(alias="displaySymbol", default=None)
    download_list: Optional["SearchCustomersDownloadList"] = Field(
        alias="downloadList", default=None
    )
    dr_account: Optional["SearchCustomersRecordRef"] = Field(
        alias="drAccount", default=None
    )
    email: Optional[str] = Field(alias="email", default=None)
    email_preference: Optional["SearchCustomersEmailPreference"] = Field(
        alias="emailPreference", default=None
    )
    email_transactions: Optional[bool] = Field(alias="emailTransactions", default=None)
    end_date: Optional[datetime.datetime] = Field(alias="endDate", default=None)
    entity_id: Optional[str] = Field(alias="entityId", default=None)
    entity_status: Optional["SearchCustomersRecordRef"] = Field(
        alias="entityStatus", default=None
    )
    estimated_budget: Optional[float] = Field(alias="estimatedBudget", default=None)
    external_id: Optional[str] = Field(alias="externalId", default=None)
    fax: Optional[str] = Field(alias="fax", default=None)
    fax_transactions: Optional[bool] = Field(alias="faxTransactions", default=None)
    first_name: Optional[str] = Field(alias="firstName", default=None)
    first_visit: Optional[datetime.datetime] = Field(alias="firstVisit", default=None)
    fx_account: Optional["SearchCustomersRecordRef"] = Field(
        alias="fxAccount", default=None
    )
    give_access: Optional[bool] = Field(alias="giveAccess", default=None)
    global_subscription_status: Optional["SearchCustomersGlobalSubscriptionStatus"] = (
        Field(alias="globalSubscriptionStatus", default=None)
    )
    group_pricing_list: Optional["SearchCustomersGroupPricingList"] = Field(
        alias="groupPricingList", default=None
    )
    home_phone: Optional[str] = Field(alias="homePhone", default=None)
    image: Optional["SearchCustomersRecordRef"] = Field(alias="image", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    is_budget_approved: Optional[bool] = Field(alias="isBudgetApproved", default=None)
    is_inactive: Optional[bool] = Field(alias="isInactive", default=None)
    is_person: Optional[bool] = Field(alias="isPerson", default=None)
    item_pricing_list: Optional["SearchCustomersItemPricingList"] = Field(
        alias="itemPricingList", default=None
    )
    keywords: Optional[str] = Field(alias="keywords", default=None)
    language: Optional["SearchCustomersLanguage"] = Field(
        alias="language", default=None
    )
    last_modified_date: Optional[datetime.datetime] = Field(
        alias="lastModifiedDate", default=None
    )
    last_name: Optional[str] = Field(alias="lastName", default=None)
    last_page_visited: Optional[str] = Field(alias="lastPageVisited", default=None)
    last_visit: Optional[datetime.datetime] = Field(alias="lastVisit", default=None)
    lead_source: Optional["SearchCustomersRecordRef"] = Field(
        alias="leadSource", default=None
    )
    middle_name: Optional[str] = Field(alias="middleName", default=None)
    mobile_phone: Optional[str] = Field(alias="mobilePhone", default=None)
    monthly_closing: Optional["SearchCustomersMonthlyClosing"] = Field(
        alias="monthlyClosing", default=None
    )
    negative_number_format: Optional["SearchCustomersNegativeNumberFormat"] = Field(
        alias="negativeNumberFormat", default=None
    )
    null_field_list: Optional["SearchCustomersNullFieldList"] = Field(
        alias="nullFieldList", default=None
    )
    number_format: Optional["SearchCustomersNumberFormat"] = Field(
        alias="numberFormat", default=None
    )
    opening_balance: Optional[float] = Field(alias="openingBalance", default=None)
    opening_balance_account: Optional["SearchCustomersRecordRef"] = Field(
        alias="openingBalanceAccount", default=None
    )
    opening_balance_date: Optional[datetime.datetime] = Field(
        alias="openingBalanceDate", default=None
    )
    overdue_balance: Optional[float] = Field(alias="overdueBalance", default=None)
    override_currency_format: Optional[bool] = Field(
        alias="overrideCurrencyFormat", default=None
    )
    parent: Optional["SearchCustomersRecordRef"] = Field(alias="parent", default=None)
    partner: Optional["SearchCustomersRecordRef"] = Field(alias="partner", default=None)
    partners_list: Optional["SearchCustomersPartnersList"] = Field(
        alias="partnersList", default=None
    )
    password: Optional[str] = Field(alias="password", default=None)
    password2: Optional[str] = Field(alias="password2", default=None)
    phone: Optional[str] = Field(alias="phone", default=None)
    phonetic_name: Optional[str] = Field(alias="phoneticName", default=None)
    pref_cc_processor: Optional["SearchCustomersRecordRef"] = Field(
        alias="prefCCProcessor", default=None
    )
    price_level: Optional["SearchCustomersRecordRef"] = Field(
        alias="priceLevel", default=None
    )
    print_on_check_as: Optional[str] = Field(alias="printOnCheckAs", default=None)
    print_transactions: Optional[bool] = Field(alias="printTransactions", default=None)
    receivables_account: Optional["SearchCustomersRecordRef"] = Field(
        alias="receivablesAccount", default=None
    )
    referrer: Optional[str] = Field(alias="referrer", default=None)
    reminder_days: Optional[int] = Field(alias="reminderDays", default=None)
    representing_subsidiary: Optional["SearchCustomersRecordRef"] = Field(
        alias="representingSubsidiary", default=None
    )
    require_pwd_change: Optional[bool] = Field(alias="requirePwdChange", default=None)
    resale_number: Optional[str] = Field(alias="resaleNumber", default=None)
    sales_group: Optional["SearchCustomersRecordRef"] = Field(
        alias="salesGroup", default=None
    )
    sales_readiness: Optional["SearchCustomersRecordRef"] = Field(
        alias="salesReadiness", default=None
    )
    sales_rep: Optional["SearchCustomersRecordRef"] = Field(
        alias="salesRep", default=None
    )
    sales_team_list: Optional["SearchCustomersSalesTeamList"] = Field(
        alias="salesTeamList", default=None
    )
    salutation: Optional[str] = Field(alias="salutation", default=None)
    send_email: Optional[bool] = Field(alias="sendEmail", default=None)
    ship_complete: Optional[bool] = Field(alias="shipComplete", default=None)
    shipping_item: Optional["SearchCustomersRecordRef"] = Field(
        alias="shippingItem", default=None
    )
    source_web_site: Optional["SearchCustomersRecordRef"] = Field(
        alias="sourceWebSite", default=None
    )
    stage: Optional["SearchCustomersStage"] = Field(alias="stage", default=None)
    start_date: Optional[datetime.datetime] = Field(alias="startDate", default=None)
    subscriptions_list: Optional["SearchCustomersSubscriptionsList"] = Field(
        alias="subscriptionsList", default=None
    )
    subsidiary: Optional["SearchCustomersRecordRef"] = Field(
        alias="subsidiary", default=None
    )
    symbol_placement: Optional["SearchCustomersSymbolPlacement"] = Field(
        alias="symbolPlacement", default=None
    )
    sync_partner_teams: Optional[bool] = Field(alias="syncPartnerTeams", default=None)
    tax_exempt: Optional[bool] = Field(alias="taxExempt", default=None)
    tax_item: Optional["SearchCustomersRecordRef"] = Field(
        alias="taxItem", default=None
    )
    tax_registration_list: Optional["SearchCustomersTaxRegistrationList"] = Field(
        alias="taxRegistrationList", default=None
    )
    taxable: Optional[bool] = Field(alias="taxable", default=None)
    terms: Optional["SearchCustomersRecordRef"] = Field(alias="terms", default=None)
    territory: Optional["SearchCustomersRecordRef"] = Field(
        alias="territory", default=None
    )
    third_party_acct: Optional[str] = Field(alias="thirdPartyAcct", default=None)
    third_party_country: Optional["SearchCustomersThirdPartyCountry"] = Field(
        alias="thirdPartyCountry", default=None
    )
    third_party_zipcode: Optional[str] = Field(alias="thirdPartyZipcode", default=None)
    title: Optional[str] = Field(alias="title", default=None)
    unbilled_orders: Optional[float] = Field(alias="unbilledOrders", default=None)
    url: Optional[str] = Field(alias="url", default=None)
    vat_reg_number: Optional[str] = Field(alias="vatRegNumber", default=None)
    visits: Optional[int] = Field(alias="visits", default=None)
    web_lead: Optional[str] = Field(alias="webLead", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchCustomers"], src_dict: Dict[str, Any]):
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
