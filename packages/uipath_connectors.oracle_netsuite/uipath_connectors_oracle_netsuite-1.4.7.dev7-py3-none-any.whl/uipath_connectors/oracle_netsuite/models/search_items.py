from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.search_items_item_carrier import SearchItemsItemCarrier
from ..models.search_items_site_category_list import SearchItemsSiteCategoryList
from ..models.search_items_item_options_list import SearchItemsItemOptionsList
from ..models.search_items_matrix_type import SearchItemsMatrixType
from ..models.search_items_out_of_stock_behavior import SearchItemsOutOfStockBehavior
from ..models.search_items_original_item_type import SearchItemsOriginalItemType
from ..models.search_items_overall_quantity_pricing_type import (
    SearchItemsOverallQuantityPricingType,
)
from ..models.search_items_item_vendor_list import SearchItemsItemVendorList
from ..models.search_items_accounting_book_detail_list import (
    SearchItemsAccountingBookDetailList,
)
from ..models.search_items_hazmat_packing_group import SearchItemsHazmatPackingGroup
from ..models.search_items_null_field_list import SearchItemsNullFieldList
from ..models.search_items_schedule_b_code import SearchItemsScheduleBCode
from ..models.search_items_product_feed_list import SearchItemsProductFeedList
from ..models.search_items_bin_number_list import SearchItemsBinNumberList
from ..models.search_items_locations_list import SearchItemsLocationsList
from ..models.search_inventory_item_record_ref import SearchInventoryItemRecordRef
from ..models.search_items_hierarchy_versions_list import (
    SearchItemsHierarchyVersionsList,
)
from ..models.search_items_translations_list import SearchItemsTranslationsList
from ..models.search_items_costing_method import SearchItemsCostingMethod
from ..models.search_items_presentation_item_list import SearchItemsPresentationItemList
from ..models.search_items_country_of_manufacture import SearchItemsCountryOfManufacture
from ..models.search_items_periodic_lot_size_type import SearchItemsPeriodicLotSizeType
from ..models.search_items_matrix_option_list import SearchItemsMatrixOptionList
from ..models.search_items_original_item_subtype import SearchItemsOriginalItemSubtype
from ..models.search_items_subsidiary_list import SearchItemsSubsidiaryList
from ..models.search_items_sitemap_priority import SearchItemsSitemapPriority
from ..models.search_items_custom_field_list import SearchItemsCustomFieldList
from ..models.search_items_vsoe_deferral import SearchItemsVsoeDeferral
from ..models.search_items_vsoe_sop_group import SearchItemsVsoeSopGroup
from ..models.search_items_preference_criterion import SearchItemsPreferenceCriterion
from ..models.search_items_fraud_risk import SearchItemsFraudRisk
from ..models.search_items_invt_classification import SearchItemsInvtClassification
from ..models.search_items_item_ship_method_list import SearchItemsItemShipMethodList
from ..models.search_items_vsoe_permit_discount import SearchItemsVsoePermitDiscount
from ..models.search_items_pricing_matrix import SearchItemsPricingMatrix
from ..models.search_items_cost_estimate_type import SearchItemsCostEstimateType
from ..models.search_items_weight_unit import SearchItemsWeightUnit


class SearchItems(BaseModel):
    """
    Attributes:
        accounting_book_detail_list (Optional[SearchItemsAccountingBookDetailList]):
        alternate_demand_source_item (Optional[SearchInventoryItemRecordRef]):
        asset_account (Optional[SearchInventoryItemRecordRef]):
        auto_lead_time (Optional[bool]): Lead time is the average number of days between ordering this item from the
                vendor and receiving it.    * Check the Auto-Calculate box if you want NetSuite to calculate the lead time based
                on the most recent order history of this item. This is calculated by taking the number of days between the order
                entry and receipt on the three most recent purchase orders, and dividing by three.          o If there are
                multiple receipts for the item against the same purchase order, only the first receipt is used for the
                calculation.          o Lead time calculation is not weighted by number of units received.          o More
                recent purchase orders without receipts are ignored.    * Clear the Auto-Calculate box to manually enter a lead
                time value in days. If the Auto-Calculate box is cleared and no value is entered, then the default value from
                the Set Up Inventory Management page is used.
        auto_preferred_stock_level (Optional[bool]): The preferred stock level is the optimum quantity to maintain in
                stock of an item.Set to true if you want NetSuite to calculate the preferred stock level based on demand for the
                item. The preferred stock level is calculated as:    (daily demand * number of days supply preferred)
        auto_reorder_point (Optional[bool]): The Reorder Point is the quantity level at which you need to reorder or
                build more of this item. Set this field to false to manually calculate the point at which to reorder or build
                more of this itemSet this field to true if you want NetSuite to calculate the reorder point based on demand for
                the item over time. The reorder point depends on the safety stock definition and is calculated as
                follows:Without safety stock defined:   Reorder point = (average lead time days * demand)With safety stock
                defined in days:    Reorder point = [(average lead time days + safety stock days) * demand]With safety stock
                quantity defined:    Reorder point = [(average lead time days * demand) + safety stock quantity)
        available_to_partners (Optional[bool]): If true, this item is available in the Advanced Partner Center.
        average_cost (Optional[float]): This field displays the current average cost of the item across all locations.
                Using the weighted-average method, the average cost is calculated as the total units available during a period
                divided by the beginning inventory cost plus the cost of additions to inventory.Note: The average cost
                calculated per location is listed for each location on the Locations subtab.If you use Multiple Units of
                Measure, average cost is calculated using stock units.
        backward_consumption_days (Optional[int]): When you use the Forecast Consumption demand source method, set the
                following:    * Forward Consumption – Number of days after the order date to consider    * Backward Consumption
                – Number of days prior to the order date to considerWhen backward and forward consumption days are entered for
                an item, these fields determine the window, or time period, that is considered for each sales order when a
                forecast amount may be consumed to calculate demand. If an order falls within the consumption window, that order
                quantity is calculated as being consumed and the forecast is adjusted to account for the order consumption.Note:
                NetSuite always considers backward consumption first.  The forecast closest to the order in the backward window
                is consumed first.The forecast closest to the order in the forward window is considered if there are remaining
                quantities to be consumed.Note: Only sales order and invoice quantities can consume forecast quantities. Demand
                from transfer orders and work orders does not consume forecast quantities.
        bill_exch_rate_variance_acct (Optional[SearchInventoryItemRecordRef]):
        bill_price_variance_acct (Optional[SearchInventoryItemRecordRef]):
        bill_qty_variance_acct (Optional[SearchInventoryItemRecordRef]):
        billing_schedule (Optional[SearchInventoryItemRecordRef]):
        bin_number_list (Optional[SearchItemsBinNumberList]):
        cogs_account (Optional[SearchInventoryItemRecordRef]):
        contingent_revenue_handling (Optional[bool]): Check this box to indicate that the item is subject to contingent
                revenue handling. When checked, revenue allocation is affected.
        copy_description (Optional[bool]): Sets the description from a sales order.
        cost (Optional[float]): Enter the price you pay for this item.If you do not enter a price, purchase orders for
                this item show the most recent purchase price by default.If you select a preferred vendor for this item, the
                price is shown in the currency selected on the vendor's record. If no preferred vendor is selected, the price is
                shown in your base currency.
        cost_category (Optional[SearchInventoryItemRecordRef]):
        cost_estimate (Optional[float]): Enter an Item Defined Cost amount.
        cost_estimate_type (Optional[SearchItemsCostEstimateType]):
        cost_estimate_units (Optional[str]):
        cost_units (Optional[str]):
        costing_method (Optional[SearchItemsCostingMethod]):
        costing_method_display (Optional[str]): This is a read-only value that returns the costing method for the item.
                Because the costingMethod field becomes read-only when set, it is not returned in get and basic search
                operations.  Instead, the read-only field CostingMethodDisplay is returned.
        country_of_manufacture (Optional[SearchItemsCountryOfManufacture]):
        create_revenue_plans_on (Optional[SearchInventoryItemRecordRef]):
        created_date (Optional[datetime.datetime]):
        currency (Optional[str]): This is a read-only field. If a preferred vendor has been specified in vendorName, the
                field returns the currency set on that vendor record. Otherwise, the base currency for the company is returned.
        custom_field_list (Optional[SearchItemsCustomFieldList]):
        custom_form (Optional[SearchInventoryItemRecordRef]):
        date_converted_to_inv (Optional[datetime.datetime]):
        default_item_ship_method (Optional[SearchInventoryItemRecordRef]):
        default_return_cost (Optional[float]): Enter the rate you want to default to show as the cost for this item when
                it is returned. What you enter in this field defaults to show in the Override Rate field on item receipts. You
                can still change this value after it appears on the item receipt.
        defer_rev_rec (Optional[bool]): Check this box to delay recognizing revenue from the sale of this item. When
                this box is check, revenue recognition schedules or revenue plans are created with the status On Hold.For more
                information, see the help topic Delaying Revenue Recognition for an Item.
        deferred_revenue_account (Optional[SearchInventoryItemRecordRef]):
        demand_modifier (Optional[float]): Set the default percentage of expected demand change to use for calculating
                item demand. For example, if you know that new customers will increase sales of this item in the future, you can
                enter 10% expected demand change to be added on to previous sales totals. If no expected demand change
                percentage is set, then the default value from the Set Up Inventory Management page is used.
        demand_source (Optional[SearchInventoryItemRecordRef]):
        demand_time_fence (Optional[int]): Demand Time Fence defaults to the number entered in the Default Demand Time
                Fence field.Verify the default or enter a number between zero and 365 to determine the demand time fence for
                this item.
        department (Optional[SearchInventoryItemRecordRef]):
        direct_revenue_posting (Optional[bool]): Check this box to disable advanced revenue management for this item.
                When checked, posting transactions that include this item post directly to the item revenue account. No revenue
                element or revenue arrangement is created. When you check this box, the Deferred Revenue Account on the
                Accounting subtab is disabled.When you create sales transactions that include items that have this box checked,
                all the items in the transaction must have the box checked. You cannot mix items that post directly to revenue
                with items that post to deferred revenue in the same transaction. This restriction also applies to kit items.
                All items in a kit must post either to revenue or to deferred revenue.You cannot check or clear the box after
                the item has been used in a transaction with advanced revenue management.By default, this box is not checked.
        display_name (Optional[str]): You can set an optional name for this item in addition to the item name. If you
                are integrating with a Yahoo! store, this field is imported from Yahoo!.The display name prints in the Item
                column of the sales form when Basic printing is used. If this item is a member of a kit, this name appears in
                the Item column when the Print Items box is checked. If you do not set a display name, then item name appears on
                printed forms.
        distribution_category (Optional[SearchInventoryItemRecordRef]):
        distribution_network (Optional[SearchInventoryItemRecordRef]):
        dont_show_price (Optional[bool]): Check this box to hide the price of this item online.This is useful for items
                you want to advertise but don't want to sell or for items that you track inventory for and want to display but
                are offered in combination with other items.
        dropship_expense_account (Optional[SearchInventoryItemRecordRef]):
        enforce_min_qty_internally (Optional[bool]): Check this box to apply the minimum quantity restriction on sales
                orders generated from NetSuite. When you clear this box, but enter a number in the Minimum Quantity field, the
                minimum quantity is only applied to web store orders.
        exclude_from_sitemap (Optional[bool]): Check this box to exclude a tab, category or item page from the site map.
        expense_account (Optional[SearchInventoryItemRecordRef]):
        external_id (Optional[str]): External Id
        featured_description (Optional[str]): Settable only if item is featured. You can provide letters, numbers and
                basic HTML code.
        fixed_lot_size (Optional[float]): If you selected Fixed Lot Size as the lot sizing method, then enter a quantity
                in the Fixed Lot Size field. This is the quantity that procurement of this item is always based on, regardless
                of demand projections.
        forward_consumption_days (Optional[int]): When you use the Forecast Consumption demand source method, set the
                following:    * Forward Consumption – Number of days after the order date to consider    * Backward Consumption
                – Number of days prior to the order date to considerWhen backward and forward consumption days are entered for
                an item, these fields determine the window, or time period, that is considered for each sales order when a
                forecast amount may be consumed to calculate demand. If an order falls within the consumption window, that order
                quantity is calculated as being consumed and the forecast is adjusted to account for the order consumption.Note:
                NetSuite always considers backward consumption first.  The forecast closest to the order in the backward window
                is consumed first.The forecast closest to the order in the forward window is considered if there are remaining
                quantities to be consumed.Note: Only sales order and invoice quantities can consume forecast quantities. Demand
                from transfer orders and work orders does not consume forecast quantities.
        fraud_risk (Optional[SearchItemsFraudRisk]):
        gain_loss_account (Optional[SearchInventoryItemRecordRef]):
        handling_cost (Optional[float]): As an option, you set a handling cost for this item in dollars. You must also
                create a shipping item for per-item shipping and handling costs at Lists > Accounting > Shipping Items > New.
                When this item is set on sales orders, invoices or cash sales, the appropriate shipping and handling charges are
                automatically calculated.
        handling_cost_units (Optional[str]):
        hazmat_hazard_class (Optional[str]): Enter the DOT hazardous material class or division.
        hazmat_id (Optional[str]): Enter the regulatory identifier for the commodity from the Federal Express Ground
                Hazardous Materials Shipping Guide.The format is UNXXXX, where XXXX is a four digit number.
        hazmat_item_units (Optional[str]): Enter the unit of measure for this item, such as kg or ml.
        hazmat_item_units_qty (Optional[float]): Enter the quantity for the item units.
        hazmat_packing_group (Optional[SearchItemsHazmatPackingGroup]):
        hazmat_shipping_name (Optional[str]): Enter the shipping name for the ID as listed in the Federal Express Ground
                Hazardous Materials Shipping Guide.This item appears on the OP950 form.
        hierarchy_versions_list (Optional[SearchItemsHierarchyVersionsList]):
        include_children (Optional[bool]): Check the Include Children box to share the item with all the sub-
                subsidiaries associated with each subsidiary selected in the Subsidiary field.Note: When sharing items across
                subsidiaries, all of the options selected on the item record must be compatible across subsidiaries. For
                example, when entering an inventory item to be shared across subsidiaries, you should select Income and Asset
                accounts on the item record that are also shared across the same subsidiaries.
        income_account (Optional[SearchInventoryItemRecordRef]):
        interco_cogs_account (Optional[SearchInventoryItemRecordRef]):
        interco_def_rev_account (Optional[SearchInventoryItemRecordRef]):
        interco_income_account (Optional[SearchInventoryItemRecordRef]):
        internal_id (Optional[str]): Internal Id which serves as primary key
        invt_classification (Optional[SearchItemsInvtClassification]):
        invt_count_interval (Optional[int]): This field displays the total number of days between required counts. For
                example, if you enter 30, the date a count is required is calculated based on 30 day intervals.
        is_donation_item (Optional[bool]): If true, the item is set as a variable-priced donation item. This enables
                customers to enter their own prices for this item, such as for donations.
        is_drop_ship_item (Optional[bool]): If isDropShipItem is set to true, isSpecialOrderItem can NOT be true.
        is_gco_compliant (Optional[bool]): Check this box to make the item available for purchase with Google Checkout.
        is_hazmat_item (Optional[bool]): Check this box if this item is categorized as either hazardous material or
                dangerous goods. These items can only be shipped using FedEx integration.
        is_inactive (Optional[bool]): Sets the item as inactive. By default, this field is set to false.
        is_online (Optional[bool]): Set to true to make this item available online in your Web site. You cannot sell
                this item online unless this field is set to true.
        is_special_order_item (Optional[bool]): If isSpecialOrderItem is set to true, isDropShipItem can NOT be true.
        is_store_pickup_allowed (Optional[bool]): If this box is checked, indicates that at least one location allows
                store pickup of the item. If you clear the Allow Store Pickup box in the Locations sublist for all locations,
                this box is also cleared when you save the item record.This field is read only.
        is_taxable (Optional[bool]): Check this box if the item is subject to sales tax.
        issue_product (Optional[SearchInventoryItemRecordRef]):
        item_carrier (Optional[SearchItemsItemCarrier]):
        item_id (Optional[str]): Type up to 60 characters for the name of this item. This name appears in lists on
                transactions.If you have the option of entering a display name and do not, the item name prints in the Item
                column of sales forms.If you have the option to enter a vendor name and do not, the item name prints in the Item
                column of purchase forms when Basic printing is used. If you have entered a display name, it will print on
                purchases instead of the item name when Basic printing is used.
        item_options_list (Optional[SearchItemsItemOptionsList]):
        item_revenue_category (Optional[SearchInventoryItemRecordRef]):
        item_ship_method_list (Optional[SearchItemsItemShipMethodList]):
        item_vendor_list (Optional[SearchItemsItemVendorList]):
        last_invt_count_date (Optional[datetime.datetime]):
        last_modified_date (Optional[datetime.datetime]):
        last_purchase_price (Optional[float]): This field displays the most recent purchase price of the item.This price
                is determined by the most recent transaction for the item that added positive inventory, such as a purchase
                receipt, inventory transfer or inventory adjustment. (This does not include item returns or assembly
                unbuilds.)If two transactions are entered on the same day, the one entered later takes precedence and is used to
                calculate the last purchase price.When you use the Multiple-Location Inventory feature, the following is true:
                * The last purchase price reflects the most recent transaction at any location.     * The Inventory subtab of
                inventory item records includes a link to the last positive-inventory transaction per location.    * If multiple
                purchases are made on the same day with different prices and locations, then the highest price paid on that day
                becomes the last purchase price.If you use Multiple Units of Measure, the last purchase price is calculated
                using purchase units.
        lead_time (Optional[int]): Lead time is the average number of days between ordering this item from the vendor
                and receiving it.    * Auto-Calculating – Check the Auto-Calculate box if you want NetSuite to calculate the
                lead time based on the most recent order history of this item. Lead time is calculated by taking the number of
                days between the order entry and receipt on the three most recent purchase orders, and dividing by three. If
                more than three purchase orders exist, all purchase orders within the period specified in the Order Analysis
                Interval field on the Inventory Management Preferences dialog will be used.          o If there are multiple
                receipts for the item against the same purchase order, the calculation is made using the difference between the
                purchase order and the last receipt (the receipt that fully receives the order).          o Lead time
                calculation is not weighted by number of units received.          o More recent purchase orders without receipts
                are ignored.    * Manually Calculating – Clear the Auto-Calculate box to manually enter a lead time value in
                days. If the Auto-Calculate box is cleared and no value is entered, then the default value from the Set Up
                Inventory Management page is used.
        location (Optional[SearchInventoryItemRecordRef]):
        locations_list (Optional[SearchItemsLocationsList]):
        manufacturer (Optional[str]): Type the name of the company that manufactures this item.
        manufacturer_addr_1 (Optional[str]): Set the address of the manufacturer. This is necessary to fill out
                international shipping forms when you sell and ship this item.
        manufacturer_city (Optional[str]): Set the city location of the manufacturer of this item. This is necessary to
                automatically fill out international forms when you ship this item across borders.
        manufacturer_state (Optional[str]): Set the state where this item's manufacturer is located.
        manufacturer_tariff (Optional[str]): Set the Harmonized System (HS) tariff code number or the Harmonized Tariff
                Schedule (HTS) code number. This number should be six to ten characters.
        manufacturer_tax_id (Optional[str]): Enter the Tax ID Number (TIN) for the manufacturer.
        manufacturer_zip (Optional[str]): Set the postal code of the location of this manufacturer.
        match_bill_to_receipt (Optional[bool]): Check the Match Bill to Receipt box if you want the Match Bill to
                Receipt box on transaction lines to be checked by default for this item. This enables you to generate variances
                based on vendor bill lines.  Then, on the Post Vendor Bill Variances page, you must select Bill in the
                Transaction Type field to generate the variance postings.Purchase orders that include this item default to have
                this box checked and variances are generated based on vendor bill lines.Clear this box if you want to generate
                variance postings based on purchase order lines rather than vendor bill lines and do not want the Match Bill to
                Receipt box to be checked by default on transaction lines for this item. Then, on the Post Vendor Bill Variances
                page, you must select Purchase Order in the Transaction Type field to generate the variance postings.This
                preference defaults to be disabled. Even when enabled, this option can be changed on individual purchase order
                lines.
        matrix_item_name_template (Optional[str]): This field is used to control how the matrix item will be displayed
                in the Matrix Item Name/Number field.Compose the order in which attributes and matrix options are displayed by
                selecting from the Insert Item Attribute and Insert Matrix Option dropdown lists.Add custom separator characters
                to easier distinguish the various options. Example: Item Name: Fabric / Color / Waist / Length [Location]
        matrix_option_list (Optional[SearchItemsMatrixOptionList]):
        matrix_type (Optional[SearchItemsMatrixType]):
        max_donation_amount (Optional[float]): If isDonationItem is set to true, set this field to the maximum amount
                that can be paid or donated for this item.
        maximum_quantity (Optional[int]): Enter the greatest quantity of this item that customers can purchase. If
                customers enter an item quantity above the maximum amount, a warning message is displayed. Web store customers
                are unable to complete checkout unless they enter a quantity equal to or below the maximum quantity. Leave this
                field empty to allow customers to check out without maximum quantity restrictions.You can edit this warning at
                Setup > Site Builder/SuiteCommerce Advanced > Customize Text.
        meta_tag_html (Optional[str]): Sets the metatag information for the item page in web store.
        minimum_quantity (Optional[int]): Enter the smallest quantity you allow customers to purchase for this item.
                When customers add this item to their carts in the Web store, the quantity for this item is defaulted to the
                minimum number of items. Leave this field empty to allow customers to check out with no minimum quantity
                restrictions.
        minimum_quantity_units (Optional[str]):
        mpn (Optional[str]): MPN (Manufacturers Part Number) - Set the part number used by the manufacturer to identify
                this item.
        mult_manufacture_addr (Optional[bool]): Check the Multiple Manufacture Addresses box if this manufacturer uses
                more than one address.
        nex_tag_category (Optional[str]): Enter the name of the NexTag category this item should be included in.This
                category is included in the product feeds you can export at Setup > Web Site > Product Feeds.Go to
                www.nextag.com for more information on the available categories.
        next_invt_count_date (Optional[datetime.datetime]): Enter the Next Inventory Count Date.NetSuite uses this
                information to calculate when that item needs to be counted.
        no_price_message (Optional[str]): If you opted to not show a price online, enter the message that should show
                instead of the price.For example, you might enter "Call for Price."
        null_field_list (Optional[SearchItemsNullFieldList]):
        offer_support (Optional[bool]): When enabled, items can be referenced on case records either through the UI or
                via web services using the item field.
        on_hand_value_mli (Optional[float]):
        on_special (Optional[bool]): Set to true if you want to put this item on special. The item then appears in the
                Specials category in your store or site.
        original_item_subtype (Optional[SearchItemsOriginalItemSubtype]):
        original_item_type (Optional[SearchItemsOriginalItemType]):
        out_of_stock_behavior (Optional[SearchItemsOutOfStockBehavior]):
        out_of_stock_message (Optional[str]): You can enter a custom out of stock message for this item. The message
                here replaces the default out of stock message.
        overall_quantity_pricing_type (Optional[SearchItemsOverallQuantityPricingType]):
        page_title (Optional[str]): Sets the display title in the upper-left corner of an Internet browser when
                customers view this item in your Web store.
        parent (Optional[SearchInventoryItemRecordRef]):
        periodic_lot_size_days (Optional[int]): In the Period of Supply Increment field, enter a number from 1 to 90.
                The default setting is 1.The increment starts on the first day an order is required. From the first day,
                NetSuite aggregates all orders in the increment. Orders are placed on the first day of the period.Note: The
                Periodic Lot Size Increment field is enabled only when you select Interval in the Periodic Lot Size Type field.
        periodic_lot_size_type (Optional[SearchItemsPeriodicLotSizeType]):
        preference_criterion (Optional[SearchItemsPreferenceCriterion]):
        preferred_location (Optional[SearchInventoryItemRecordRef]):
        preferred_stock_level (Optional[float]): Sets the preferred quantity to maintain in inventory. NetSuite uses
                this information to calculate how many items to replenish on the Order Items page. If the Multi-Locations
                Inventory feature is enabled, provide values for each location using the locationsList element.
        preferred_stock_level_days (Optional[float]): The preferred stock level is the optimum quantity to maintain in
                stock of an item.The quantity you enter here is used to determine your replenishment needs on the Order Items
                page. It is the quantity you want to have in stock after an order is placed.    * Auto-Calculating – Check the
                Auto-Calculate box if you want NetSuite to calculate the preferred stock level based on demand for the item.
                The preferred stock level is calculated as:      (daily demand * number of days supply preferred).      If no
                preferred stock level is identified, then the default preferred stock level is used from the Set Up Inventory
                Management page.    * Manually Calculating – Clear the Auto-Calculate box to manually enter the preferred stock
                quantity.The preferred stock level you set is used to calculate the quantity of items to be ordered on the Order
                Items page.
        preferred_stock_level_units (Optional[str]):
        presentation_item_list (Optional[SearchItemsPresentationItemList]):
        prices_include_tax (Optional[bool]): Check this box to save the base price as the tax inclusive price. Clear
                this box to save the base price as the tax exclusive price.
        pricing_group (Optional[SearchInventoryItemRecordRef]):
        pricing_matrix (Optional[SearchItemsPricingMatrix]):
        producer (Optional[bool]): Set to true if you produce this item for the purposes of the NAFTA Certificate of
                Origin.
        product_feed_list (Optional[SearchItemsProductFeedList]):
        purchase_description (Optional[str]): Sets the description of this item that is displayed on vendor orders. You
                should include the unit of measure in this description.
        purchase_order_amount (Optional[float]): Enter the tolerance limit for the discrepancy between the amount on the
                vendor bill and purchase order.
        purchase_order_quantity (Optional[float]): Enter the tolerance limit for the discrepancy between the quantity on
                the vendor bill and purchase order.
        purchase_order_quantity_diff (Optional[float]): Enter the difference limit for the discrepancy between the
                quantity on the vendor bill and purchase order.
        purchase_price_variance_acct (Optional[SearchInventoryItemRecordRef]):
        purchase_tax_code (Optional[SearchInventoryItemRecordRef]):
        purchase_unit (Optional[SearchInventoryItemRecordRef]):
        quantity_available (Optional[float]):
        quantity_available_units (Optional[str]):
        quantity_back_ordered (Optional[float]):
        quantity_committed (Optional[float]): This is a read-only field that returns the number of items committed to be
                sold and are currently showing on orders.If the Multi-Location Inventory feature is enabled, you must provide a
                list of quantityCommitted values for each location as needed using the locationsList element.
        quantity_committed_units (Optional[str]):
        quantity_on_hand (Optional[float]): Sets the quantity on hand for this item. This is settable only on an add.
                Otherwise this is a read-only field that provides the known quantity on hand based on items received. If the
                Multi-Location Inventory feature is enabled, you must provide a list of quantity on hand values for each
                location as needed using the locationsList element.
        quantity_on_hand_units (Optional[str]):
        quantity_on_order (Optional[float]): A read-only field that returns the quantity of this item you currently have
                on order with the vendor.If the Multi-Location Inventory feature is enabled, you must provide a list of
                quantityOnOrder values for each location as needed using the locationsList element.
        quantity_on_order_units (Optional[str]):
        quantity_pricing_schedule (Optional[SearchInventoryItemRecordRef]):
        quantity_reorder_units (Optional[str]):
        rate (Optional[float]): Defines the rate for this item. If a value is entered followed by the percentage sign,
                the discount is interpreted as a percentage discount (i.e.  -.10% sets a ten percent discount for the item). If
                a value without the percentage sign is entered, the rate is interpreted as a flat dollar value.
        receipt_amount (Optional[float]): Enter the tolerance limit for the discrepancy between the amount on the vendor
                bill and item receipt.
        receipt_quantity (Optional[float]): Enter the tolerance limit for the discrepancy between the quantity on the
                vendor bill and item receipt.
        receipt_quantity_diff (Optional[float]): Enter the difference limit for the discrepancy between the quantity on
                the vendor bill and item receipt.
        related_items_description (Optional[str]): Sets the description displayed for a group of related items.
        reorder_multiple (Optional[int]): Enter the quantity you prefer to order of this item each time. Then, the Order
                Items page suggests ordering a quantity of this item that is always multiple of the number you enter.For
                example, if the vendor only accepts orders in multiples of one thousand, you would enter 1000 in this field.
                Then, the Order items page might suggest that you order 1000 or 2000, but not 1500.Note: If you use the Multiple
                Units of Measure feature, the reorder multiple always functions in base units.
        reorder_point (Optional[float]): Sets the minimum quantity that when reached triggers a warning to reorder or
                rebuild this item. If the Multi-Location Inventory feature is enabled, this field should be populated for each
                location using the locationsList element.
        reorder_point_units (Optional[str]):
        reschedule_in_days (Optional[int]): In the Reschedule In Days field, enter a number between one and 90 that is
                the maximum number of days that the order can be advanced from the current day. For example, if you enter 10 in
                this field, an order for this item can be moved up ten days earlier, but not eleven or more days. This field
                defaults to be blank.Note: If this field is left blank, NetSuite does not make recommendations to reschedule
                orders for this item to a later date.
        reschedule_out_days (Optional[int]): In the Reschedule Out Days field, enter a number between one and 180 that
                is the maximum number of days that the order can be delayed from the current day. For example, if you enter 10
                in this field, an order for this item can be moved to ten days later, but not eleven or more days. This field
                defaults to be blank.Note: If this field is left blank, NetSuite does not make recommendations to reschedule
                orders for this item to a later date.
        rev_rec_forecast_rule (Optional[SearchInventoryItemRecordRef]):
        rev_rec_schedule (Optional[SearchInventoryItemRecordRef]):
        rev_reclass_fx_account (Optional[SearchInventoryItemRecordRef]):
        revenue_allocation_group (Optional[SearchInventoryItemRecordRef]):
        revenue_recognition_rule (Optional[SearchInventoryItemRecordRef]):
        round_up_as_component (Optional[bool]): If you use the component yield preference, depending on your settings,
                the component yield calculation may result in a fractional quantity. You can use this setting so that the
                quantity for a component on a work order automatically rounds up to a whole number in base units.For example,
                you have an assembly that requires 2 units of Component A. The component yield is 99%. To build 5 of these
                assemblies requires 10.1 units of Component A. Since you can consume components only in whole numbers, you
                cannot consume 10.1 units. Therefore, you need to round up to the next highest whole number in base units.Check
                the Round Up Quantity as Component box to enable NetSuite to round up the quantity consumed for this item.Clear
                this box if you do not want NetSuite to round up the quantity consumed for this item.
        safety_stock_level (Optional[float]): Enter the amount of an item you prefer to keep in stock at all times.
                Safety stock can be a quantity or a number of days worth of stock. This amount is used to auto-calculate the
                reorder point of an item.    * To define safety stock as a quantity, enter a value.    * To define safety stock
                as a number of days, enter a value in the field next to Days.If no safety stock value is entered, then the
                default value from the Set Up Inventory Management page is used.
        safety_stock_level_days (Optional[int]): Enter the amount of an item you prefer to keep in stock at all times.
                Safety stock can be a quantity or a number of days worth of stock. This amount is used to auto-calculate the
                reorder point of an item.    * To define safety stock as a quantity, enter a value.    * To define safety stock
                as a number of days, enter a value in the field next to Days.If no safety stock value is entered, then the
                default value from the Set Up Inventory Management page is used.
        safety_stock_level_units (Optional[str]):
        sale_unit (Optional[SearchInventoryItemRecordRef]):
        sales_description (Optional[str]): Sets the description displayed when an item's store display name is clicked.
        sales_tax_code (Optional[SearchInventoryItemRecordRef]):
        schedule_b_code (Optional[SearchItemsScheduleBCode]):
        schedule_b_number (Optional[str]): Enter the number for the Schedule B form for this item.
        schedule_b_quantity (Optional[int]): Enter the quantity for the Schedule B form for this item.
        search_keywords (Optional[str]): Enter alternative search keywords that customers might use to find this item
                using your Web store�s internal search. These can include synonyms, acronyms, alternate languages or
                misspellings. These keywords are seen as equally important as the item name when searches are conducted.
        seasonal_demand (Optional[bool]): Check the Seasonal Demand box to define how NetSuite analyzes customer demand
                for this item.Customer demand for an item is used to auto-calculate reorder points and preferred stock levels.
                An item’s demand rate is calculated as the average sales quantity per day.    * Historical Demand – Clear the
                Seasonal Demand box to calculate the demand as average sales per day over a specific period.      To set the
                number of months interval between analysis to evaluate sales orders and calculate item demand, go to Setup >
                Accounting > Set Up Inventory Management > Order Analysis Interval field.    * Seasonal Demand – Check the
                Seasonal Demand box to calculate the reorder quantity for this item based on inventory demand changes through
                the year.      To set the number of months interval between analysis to evaluate sales orders and calculate item
                demand, go to Setup > Accounting > Set Up Inventory Management > Order Analysis Interval field.
        ship_individually (Optional[bool]): Check this box if this item always ships alone and with no other items in
                the same package.This helps determine the number of packages needed and the shipping rate on order fulfillments.
        ship_package (Optional[SearchInventoryItemRecordRef]):
        shipping_cost (Optional[float]): As an option, you may set a shipping cost for this item in dollars. You must
                also create a shipping item for per-item shipping costs at Lists > Accounting > Shipping Items > New. When this
                item is set on sales orders, invoices or cash sales, the appropriate shipping charges are automatically
                calculated.
        shipping_cost_units (Optional[str]):
        shopping_dot_com_category (Optional[str]): Enter the name of the Shopping.com category that this item should go
                under.This category is included in the product feeds that you can export from Setup > Web Site > Product
                Feeds.Go to www.shopping.com for more information on the categories available.
        shopzilla_category_id (Optional[int]): Enter the name of the Shopzilla category this item should be included
                in.This category is included in the product feeds you export at Setup > Web Site > Product Feeds.Go to
                www.shopzilla.com for more information on the available categories.
        show_default_donation_amount (Optional[bool]): Can only be set when isDonation is set to True. If true, the
                item's online price is displayed as a suggested price.
        site_category_list (Optional[SearchItemsSiteCategoryList]):
        sitemap_priority (Optional[SearchItemsSitemapPriority]):
        soft_descriptor (Optional[SearchInventoryItemRecordRef]):
        specials_description (Optional[str]): Settable only if onSpecial is set to True. You can provide letters,
                numbers and basic HTML code.
        stock_description (Optional[str]): Enter up to 21 characters to specify information about this item, such as
                New, Refurbished or Ships 2-3 days.
        stock_unit (Optional[SearchInventoryItemRecordRef]):
        store_description (Optional[str]): Sets the item description. This field can contain plain text as well as basic
                html code.
        store_detailed_description (Optional[str]): Sets the detailed item description. This field can contain plain
                text as well as basic html code.
        store_display_image (Optional[SearchInventoryItemRecordRef]):
        store_display_name (Optional[str]): Sets the item name for your Web site.
        store_display_thumbnail (Optional[SearchInventoryItemRecordRef]):
        store_item_template (Optional[SearchInventoryItemRecordRef]):
        subsidiary_list (Optional[SearchItemsSubsidiaryList]):
        supply_lot_sizing_method (Optional[SearchInventoryItemRecordRef]):
        supply_replenishment_method (Optional[SearchInventoryItemRecordRef]):
        supply_time_fence (Optional[int]): This field defaults to the number entered in the Default Planning Time Fence
                field. Verify the default or enter a number between zero and 365 to determine the planning time fence for this
                item.
        supply_type (Optional[SearchInventoryItemRecordRef]):
        tax_schedule (Optional[SearchInventoryItemRecordRef]):
        total_value (Optional[float]): By default this field is the result of multiplying the purchase price by the
                quantity on hand. If the Multi-Location Inventory feature is enabled, the sum of this result for each location
                populates this field by default.
        track_landed_cost (Optional[bool]): Set to true to track landed costs associated with this item.Note: You must
                include an item that tracks landed costs on transactions you want to source for landed costs.
        transfer_price (Optional[float]): Enter a transfer price on an item record to set the default value used as the
                transfer price on transfer orders. You can still override this default by entering a new transfer price for an
                item on the transfer order.The use of the value in the Transfer Price field on a transfer order depends on your
                setting for the Use Item Cost as Transfer Cost preference.When the Use Item Cost as Transfer Cost preference is
                enabled, the transfer price on a transfer order is not considered for posting cost accounting of line items. In
                the Transfer Price field, enter a declared value for the item to be used for shipping purposes only.When the Use
                Item Cost as Transfer Cost preference is disabled, the transfer price on a transfer order is considered for
                posting cost accounting of line items. Items that do not have a transfer price set on a transfer order use a
                zero value for cost accounting calculations when the item is received.Note: If the Transfer Price field is blank
                on the item record, a value of zero shows by default on the transfer order. Unless a transfer price value is
                entered on the transfer order, a value of zero is used for COGS calculations when the item is received.
        translations_list (Optional[SearchItemsTranslationsList]):
        units_type (Optional[SearchInventoryItemRecordRef]):
        upc_code (Optional[str]): Defines whether this is a unv part code. Bar codes for items are generated in Code 128
                by default. If you prefer to use the UPC code format, set this field to True on each item record.
        url_component (Optional[str]): Enter a short, descriptive name for this item to appear as part of its URL in the
                Web store.Setting a name to show in the URL can result in better ranking from search engines.If you leave this
                field blank, NetSuite terms and numbers are used as identifiers in the URL.Note: Descriptive URL components are
                case sensitive. Descriptive URLs must match the case used in the URL Component field of an item record to point
                to the correct page.
        use_bins (Optional[bool]): Set to true if you want to track bin locations for this item. If you choose to use
                bins for this item, you must associate at least one bin with the item using the Bin Numbers subtab. You can
                associate multiple items with one bin and multiple bins with one item. You can also designate one preferred bin
                per location. The preferred bin is listed by default on receipt and fulfillment transactions. To create bin
                records that can be entered here, go to Lists > Accounting > Bins > New.
        use_marginal_rates (Optional[bool]): Set to true if you want the quantity discounts in the schedule to be
                applied to each pricing bracket separately.For example, a schedule offers no discount for the first 100 items
                sold and a 5% discount if more than 100 are sold. If 150 items are sold, the first 100 are at normal price, and
                the other fifty items are sold at 5% discount.The fault value is false, which applies the discount to all items
                sold.
        vendor (Optional[SearchInventoryItemRecordRef]):
        vendor_name (Optional[str]): Sets the preferred vendor for this item. If the Multiple Vendors feature is
                enabled, this field is unavailable and you must set the preferred vendor in the itemVendorsList.
        vsoe_deferral (Optional[SearchItemsVsoeDeferral]):
        vsoe_delivered (Optional[bool]): Check this box to automatically set this item to a Delivered status when this
                item is added to a transaction. Clear this box to leave the delivery status clear by default.
        vsoe_permit_discount (Optional[SearchItemsVsoePermitDiscount]):
        vsoe_price (Optional[float]): Set the VSOE price for this item, if the price is known.Note: If you need to use
                more than one VSOE price for an item, you can set the most common price here and then change the price on each
                order manually.
        vsoe_sop_group (Optional[SearchItemsVsoeSopGroup]):
        weight (Optional[float]): Set the weight of this item
        weight_unit (Optional[SearchItemsWeightUnit]):
        weight_units (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    accounting_book_detail_list: Optional["SearchItemsAccountingBookDetailList"] = (
        Field(alias="accountingBookDetailList", default=None)
    )
    alternate_demand_source_item: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="alternateDemandSourceItem", default=None
    )
    asset_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="assetAccount", default=None
    )
    auto_lead_time: Optional[bool] = Field(alias="autoLeadTime", default=None)
    auto_preferred_stock_level: Optional[bool] = Field(
        alias="autoPreferredStockLevel", default=None
    )
    auto_reorder_point: Optional[bool] = Field(alias="autoReorderPoint", default=None)
    available_to_partners: Optional[bool] = Field(
        alias="availableToPartners", default=None
    )
    average_cost: Optional[float] = Field(alias="averageCost", default=None)
    backward_consumption_days: Optional[int] = Field(
        alias="backwardConsumptionDays", default=None
    )
    bill_exch_rate_variance_acct: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="billExchRateVarianceAcct", default=None
    )
    bill_price_variance_acct: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="billPriceVarianceAcct", default=None
    )
    bill_qty_variance_acct: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="billQtyVarianceAcct", default=None
    )
    billing_schedule: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="billingSchedule", default=None
    )
    bin_number_list: Optional["SearchItemsBinNumberList"] = Field(
        alias="binNumberList", default=None
    )
    cogs_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="cogsAccount", default=None
    )
    contingent_revenue_handling: Optional[bool] = Field(
        alias="contingentRevenueHandling", default=None
    )
    copy_description: Optional[bool] = Field(alias="copyDescription", default=None)
    cost: Optional[float] = Field(alias="cost", default=None)
    cost_category: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="costCategory", default=None
    )
    cost_estimate: Optional[float] = Field(alias="costEstimate", default=None)
    cost_estimate_type: Optional["SearchItemsCostEstimateType"] = Field(
        alias="costEstimateType", default=None
    )
    cost_estimate_units: Optional[str] = Field(alias="costEstimateUnits", default=None)
    cost_units: Optional[str] = Field(alias="costUnits", default=None)
    costing_method: Optional["SearchItemsCostingMethod"] = Field(
        alias="costingMethod", default=None
    )
    costing_method_display: Optional[str] = Field(
        alias="costingMethodDisplay", default=None
    )
    country_of_manufacture: Optional["SearchItemsCountryOfManufacture"] = Field(
        alias="countryOfManufacture", default=None
    )
    create_revenue_plans_on: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="createRevenuePlansOn", default=None
    )
    created_date: Optional[datetime.datetime] = Field(alias="createdDate", default=None)
    currency: Optional[str] = Field(alias="currency", default=None)
    custom_field_list: Optional["SearchItemsCustomFieldList"] = Field(
        alias="customFieldList", default=None
    )
    custom_form: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="customForm", default=None
    )
    date_converted_to_inv: Optional[datetime.datetime] = Field(
        alias="dateConvertedToInv", default=None
    )
    default_item_ship_method: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="defaultItemShipMethod", default=None
    )
    default_return_cost: Optional[float] = Field(
        alias="defaultReturnCost", default=None
    )
    defer_rev_rec: Optional[bool] = Field(alias="deferRevRec", default=None)
    deferred_revenue_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="deferredRevenueAccount", default=None
    )
    demand_modifier: Optional[float] = Field(alias="demandModifier", default=None)
    demand_source: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="demandSource", default=None
    )
    demand_time_fence: Optional[int] = Field(alias="demandTimeFence", default=None)
    department: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="department", default=None
    )
    direct_revenue_posting: Optional[bool] = Field(
        alias="directRevenuePosting", default=None
    )
    display_name: Optional[str] = Field(alias="displayName", default=None)
    distribution_category: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="distributionCategory", default=None
    )
    distribution_network: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="distributionNetwork", default=None
    )
    dont_show_price: Optional[bool] = Field(alias="dontShowPrice", default=None)
    dropship_expense_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="dropshipExpenseAccount", default=None
    )
    enforce_min_qty_internally: Optional[bool] = Field(
        alias="enforceMinQtyInternally", default=None
    )
    exclude_from_sitemap: Optional[bool] = Field(
        alias="excludeFromSitemap", default=None
    )
    expense_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="expenseAccount", default=None
    )
    external_id: Optional[str] = Field(alias="externalId", default=None)
    featured_description: Optional[str] = Field(
        alias="featuredDescription", default=None
    )
    fixed_lot_size: Optional[float] = Field(alias="fixedLotSize", default=None)
    forward_consumption_days: Optional[int] = Field(
        alias="forwardConsumptionDays", default=None
    )
    fraud_risk: Optional["SearchItemsFraudRisk"] = Field(
        alias="fraudRisk", default=None
    )
    gain_loss_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="gainLossAccount", default=None
    )
    handling_cost: Optional[float] = Field(alias="handlingCost", default=None)
    handling_cost_units: Optional[str] = Field(alias="handlingCostUnits", default=None)
    hazmat_hazard_class: Optional[str] = Field(alias="hazmatHazardClass", default=None)
    hazmat_id: Optional[str] = Field(alias="hazmatId", default=None)
    hazmat_item_units: Optional[str] = Field(alias="hazmatItemUnits", default=None)
    hazmat_item_units_qty: Optional[float] = Field(
        alias="hazmatItemUnitsQty", default=None
    )
    hazmat_packing_group: Optional["SearchItemsHazmatPackingGroup"] = Field(
        alias="hazmatPackingGroup", default=None
    )
    hazmat_shipping_name: Optional[str] = Field(
        alias="hazmatShippingName", default=None
    )
    hierarchy_versions_list: Optional["SearchItemsHierarchyVersionsList"] = Field(
        alias="hierarchyVersionsList", default=None
    )
    include_children: Optional[bool] = Field(alias="includeChildren", default=None)
    income_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="incomeAccount", default=None
    )
    interco_cogs_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="intercoCogsAccount", default=None
    )
    interco_def_rev_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="intercoDefRevAccount", default=None
    )
    interco_income_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="intercoIncomeAccount", default=None
    )
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    invt_classification: Optional["SearchItemsInvtClassification"] = Field(
        alias="invtClassification", default=None
    )
    invt_count_interval: Optional[int] = Field(alias="invtCountInterval", default=None)
    is_donation_item: Optional[bool] = Field(alias="isDonationItem", default=None)
    is_drop_ship_item: Optional[bool] = Field(alias="isDropShipItem", default=None)
    is_gco_compliant: Optional[bool] = Field(alias="isGcoCompliant", default=None)
    is_hazmat_item: Optional[bool] = Field(alias="isHazmatItem", default=None)
    is_inactive: Optional[bool] = Field(alias="isInactive", default=None)
    is_online: Optional[bool] = Field(alias="isOnline", default=None)
    is_special_order_item: Optional[bool] = Field(
        alias="isSpecialOrderItem", default=None
    )
    is_store_pickup_allowed: Optional[bool] = Field(
        alias="isStorePickupAllowed", default=None
    )
    is_taxable: Optional[bool] = Field(alias="isTaxable", default=None)
    issue_product: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="issueProduct", default=None
    )
    item_carrier: Optional["SearchItemsItemCarrier"] = Field(
        alias="itemCarrier", default=None
    )
    item_id: Optional[str] = Field(alias="itemId", default=None)
    item_options_list: Optional["SearchItemsItemOptionsList"] = Field(
        alias="itemOptionsList", default=None
    )
    item_revenue_category: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="itemRevenueCategory", default=None
    )
    item_ship_method_list: Optional["SearchItemsItemShipMethodList"] = Field(
        alias="itemShipMethodList", default=None
    )
    item_vendor_list: Optional["SearchItemsItemVendorList"] = Field(
        alias="itemVendorList", default=None
    )
    last_invt_count_date: Optional[datetime.datetime] = Field(
        alias="lastInvtCountDate", default=None
    )
    last_modified_date: Optional[datetime.datetime] = Field(
        alias="lastModifiedDate", default=None
    )
    last_purchase_price: Optional[float] = Field(
        alias="lastPurchasePrice", default=None
    )
    lead_time: Optional[int] = Field(alias="leadTime", default=None)
    location: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="location", default=None
    )
    locations_list: Optional["SearchItemsLocationsList"] = Field(
        alias="locationsList", default=None
    )
    manufacturer: Optional[str] = Field(alias="manufacturer", default=None)
    manufacturer_addr_1: Optional[str] = Field(alias="manufacturerAddr1", default=None)
    manufacturer_city: Optional[str] = Field(alias="manufacturerCity", default=None)
    manufacturer_state: Optional[str] = Field(alias="manufacturerState", default=None)
    manufacturer_tariff: Optional[str] = Field(alias="manufacturerTariff", default=None)
    manufacturer_tax_id: Optional[str] = Field(alias="manufacturerTaxId", default=None)
    manufacturer_zip: Optional[str] = Field(alias="manufacturerZip", default=None)
    match_bill_to_receipt: Optional[bool] = Field(
        alias="matchBillToReceipt", default=None
    )
    matrix_item_name_template: Optional[str] = Field(
        alias="matrixItemNameTemplate", default=None
    )
    matrix_option_list: Optional["SearchItemsMatrixOptionList"] = Field(
        alias="matrixOptionList", default=None
    )
    matrix_type: Optional["SearchItemsMatrixType"] = Field(
        alias="matrixType", default=None
    )
    max_donation_amount: Optional[float] = Field(
        alias="maxDonationAmount", default=None
    )
    maximum_quantity: Optional[int] = Field(alias="maximumQuantity", default=None)
    meta_tag_html: Optional[str] = Field(alias="metaTagHtml", default=None)
    minimum_quantity: Optional[int] = Field(alias="minimumQuantity", default=None)
    minimum_quantity_units: Optional[str] = Field(
        alias="minimumQuantityUnits", default=None
    )
    mpn: Optional[str] = Field(alias="mpn", default=None)
    mult_manufacture_addr: Optional[bool] = Field(
        alias="multManufactureAddr", default=None
    )
    nex_tag_category: Optional[str] = Field(alias="nexTagCategory", default=None)
    next_invt_count_date: Optional[datetime.datetime] = Field(
        alias="nextInvtCountDate", default=None
    )
    no_price_message: Optional[str] = Field(alias="noPriceMessage", default=None)
    null_field_list: Optional["SearchItemsNullFieldList"] = Field(
        alias="nullFieldList", default=None
    )
    offer_support: Optional[bool] = Field(alias="offerSupport", default=None)
    on_hand_value_mli: Optional[float] = Field(alias="onHandValueMli", default=None)
    on_special: Optional[bool] = Field(alias="onSpecial", default=None)
    original_item_subtype: Optional["SearchItemsOriginalItemSubtype"] = Field(
        alias="originalItemSubtype", default=None
    )
    original_item_type: Optional["SearchItemsOriginalItemType"] = Field(
        alias="originalItemType", default=None
    )
    out_of_stock_behavior: Optional["SearchItemsOutOfStockBehavior"] = Field(
        alias="outOfStockBehavior", default=None
    )
    out_of_stock_message: Optional[str] = Field(alias="outOfStockMessage", default=None)
    overall_quantity_pricing_type: Optional["SearchItemsOverallQuantityPricingType"] = (
        Field(alias="overallQuantityPricingType", default=None)
    )
    page_title: Optional[str] = Field(alias="pageTitle", default=None)
    parent: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="parent", default=None
    )
    periodic_lot_size_days: Optional[int] = Field(
        alias="periodicLotSizeDays", default=None
    )
    periodic_lot_size_type: Optional["SearchItemsPeriodicLotSizeType"] = Field(
        alias="periodicLotSizeType", default=None
    )
    preference_criterion: Optional["SearchItemsPreferenceCriterion"] = Field(
        alias="preferenceCriterion", default=None
    )
    preferred_location: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="preferredLocation", default=None
    )
    preferred_stock_level: Optional[float] = Field(
        alias="preferredStockLevel", default=None
    )
    preferred_stock_level_days: Optional[float] = Field(
        alias="preferredStockLevelDays", default=None
    )
    preferred_stock_level_units: Optional[str] = Field(
        alias="preferredStockLevelUnits", default=None
    )
    presentation_item_list: Optional["SearchItemsPresentationItemList"] = Field(
        alias="presentationItemList", default=None
    )
    prices_include_tax: Optional[bool] = Field(alias="pricesIncludeTax", default=None)
    pricing_group: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="pricingGroup", default=None
    )
    pricing_matrix: Optional["SearchItemsPricingMatrix"] = Field(
        alias="pricingMatrix", default=None
    )
    producer: Optional[bool] = Field(alias="producer", default=None)
    product_feed_list: Optional["SearchItemsProductFeedList"] = Field(
        alias="productFeedList", default=None
    )
    purchase_description: Optional[str] = Field(
        alias="purchaseDescription", default=None
    )
    purchase_order_amount: Optional[float] = Field(
        alias="purchaseOrderAmount", default=None
    )
    purchase_order_quantity: Optional[float] = Field(
        alias="purchaseOrderQuantity", default=None
    )
    purchase_order_quantity_diff: Optional[float] = Field(
        alias="purchaseOrderQuantityDiff", default=None
    )
    purchase_price_variance_acct: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="purchasePriceVarianceAcct", default=None
    )
    purchase_tax_code: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="purchaseTaxCode", default=None
    )
    purchase_unit: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="purchaseUnit", default=None
    )
    quantity_available: Optional[float] = Field(alias="quantityAvailable", default=None)
    quantity_available_units: Optional[str] = Field(
        alias="quantityAvailableUnits", default=None
    )
    quantity_back_ordered: Optional[float] = Field(
        alias="quantityBackOrdered", default=None
    )
    quantity_committed: Optional[float] = Field(alias="quantityCommitted", default=None)
    quantity_committed_units: Optional[str] = Field(
        alias="quantityCommittedUnits", default=None
    )
    quantity_on_hand: Optional[float] = Field(alias="quantityOnHand", default=None)
    quantity_on_hand_units: Optional[str] = Field(
        alias="quantityOnHandUnits", default=None
    )
    quantity_on_order: Optional[float] = Field(alias="quantityOnOrder", default=None)
    quantity_on_order_units: Optional[str] = Field(
        alias="quantityOnOrderUnits", default=None
    )
    quantity_pricing_schedule: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="quantityPricingSchedule", default=None
    )
    quantity_reorder_units: Optional[str] = Field(
        alias="quantityReorderUnits", default=None
    )
    rate: Optional[float] = Field(alias="rate", default=None)
    receipt_amount: Optional[float] = Field(alias="receiptAmount", default=None)
    receipt_quantity: Optional[float] = Field(alias="receiptQuantity", default=None)
    receipt_quantity_diff: Optional[float] = Field(
        alias="receiptQuantityDiff", default=None
    )
    related_items_description: Optional[str] = Field(
        alias="relatedItemsDescription", default=None
    )
    reorder_multiple: Optional[int] = Field(alias="reorderMultiple", default=None)
    reorder_point: Optional[float] = Field(alias="reorderPoint", default=None)
    reorder_point_units: Optional[str] = Field(alias="reorderPointUnits", default=None)
    reschedule_in_days: Optional[int] = Field(alias="rescheduleInDays", default=None)
    reschedule_out_days: Optional[int] = Field(alias="rescheduleOutDays", default=None)
    rev_rec_forecast_rule: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="revRecForecastRule", default=None
    )
    rev_rec_schedule: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="revRecSchedule", default=None
    )
    rev_reclass_fx_account: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="revReclassFXAccount", default=None
    )
    revenue_allocation_group: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="revenueAllocationGroup", default=None
    )
    revenue_recognition_rule: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="revenueRecognitionRule", default=None
    )
    round_up_as_component: Optional[bool] = Field(
        alias="roundUpAsComponent", default=None
    )
    safety_stock_level: Optional[float] = Field(alias="safetyStockLevel", default=None)
    safety_stock_level_days: Optional[int] = Field(
        alias="safetyStockLevelDays", default=None
    )
    safety_stock_level_units: Optional[str] = Field(
        alias="safetyStockLevelUnits", default=None
    )
    sale_unit: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="saleUnit", default=None
    )
    sales_description: Optional[str] = Field(alias="salesDescription", default=None)
    sales_tax_code: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="salesTaxCode", default=None
    )
    schedule_b_code: Optional["SearchItemsScheduleBCode"] = Field(
        alias="scheduleBCode", default=None
    )
    schedule_b_number: Optional[str] = Field(alias="scheduleBNumber", default=None)
    schedule_b_quantity: Optional[int] = Field(alias="scheduleBQuantity", default=None)
    search_keywords: Optional[str] = Field(alias="searchKeywords", default=None)
    seasonal_demand: Optional[bool] = Field(alias="seasonalDemand", default=None)
    ship_individually: Optional[bool] = Field(alias="shipIndividually", default=None)
    ship_package: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="shipPackage", default=None
    )
    shipping_cost: Optional[float] = Field(alias="shippingCost", default=None)
    shipping_cost_units: Optional[str] = Field(alias="shippingCostUnits", default=None)
    shopping_dot_com_category: Optional[str] = Field(
        alias="shoppingDotComCategory", default=None
    )
    shopzilla_category_id: Optional[int] = Field(
        alias="shopzillaCategoryId", default=None
    )
    show_default_donation_amount: Optional[bool] = Field(
        alias="showDefaultDonationAmount", default=None
    )
    site_category_list: Optional["SearchItemsSiteCategoryList"] = Field(
        alias="siteCategoryList", default=None
    )
    sitemap_priority: Optional["SearchItemsSitemapPriority"] = Field(
        alias="sitemapPriority", default=None
    )
    soft_descriptor: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="softDescriptor", default=None
    )
    specials_description: Optional[str] = Field(
        alias="specialsDescription", default=None
    )
    stock_description: Optional[str] = Field(alias="stockDescription", default=None)
    stock_unit: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="stockUnit", default=None
    )
    store_description: Optional[str] = Field(alias="storeDescription", default=None)
    store_detailed_description: Optional[str] = Field(
        alias="storeDetailedDescription", default=None
    )
    store_display_image: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="storeDisplayImage", default=None
    )
    store_display_name: Optional[str] = Field(alias="storeDisplayName", default=None)
    store_display_thumbnail: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="storeDisplayThumbnail", default=None
    )
    store_item_template: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="storeItemTemplate", default=None
    )
    subsidiary_list: Optional["SearchItemsSubsidiaryList"] = Field(
        alias="subsidiaryList", default=None
    )
    supply_lot_sizing_method: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="supplyLotSizingMethod", default=None
    )
    supply_replenishment_method: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="supplyReplenishmentMethod", default=None
    )
    supply_time_fence: Optional[int] = Field(alias="supplyTimeFence", default=None)
    supply_type: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="supplyType", default=None
    )
    tax_schedule: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="taxSchedule", default=None
    )
    total_value: Optional[float] = Field(alias="totalValue", default=None)
    track_landed_cost: Optional[bool] = Field(alias="trackLandedCost", default=None)
    transfer_price: Optional[float] = Field(alias="transferPrice", default=None)
    translations_list: Optional["SearchItemsTranslationsList"] = Field(
        alias="translationsList", default=None
    )
    units_type: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="unitsType", default=None
    )
    upc_code: Optional[str] = Field(alias="upcCode", default=None)
    url_component: Optional[str] = Field(alias="urlComponent", default=None)
    use_bins: Optional[bool] = Field(alias="useBins", default=None)
    use_marginal_rates: Optional[bool] = Field(alias="useMarginalRates", default=None)
    vendor: Optional["SearchInventoryItemRecordRef"] = Field(
        alias="vendor", default=None
    )
    vendor_name: Optional[str] = Field(alias="vendorName", default=None)
    vsoe_deferral: Optional["SearchItemsVsoeDeferral"] = Field(
        alias="vsoeDeferral", default=None
    )
    vsoe_delivered: Optional[bool] = Field(alias="vsoeDelivered", default=None)
    vsoe_permit_discount: Optional["SearchItemsVsoePermitDiscount"] = Field(
        alias="vsoePermitDiscount", default=None
    )
    vsoe_price: Optional[float] = Field(alias="vsoePrice", default=None)
    vsoe_sop_group: Optional["SearchItemsVsoeSopGroup"] = Field(
        alias="vsoeSopGroup", default=None
    )
    weight: Optional[float] = Field(alias="weight", default=None)
    weight_unit: Optional["SearchItemsWeightUnit"] = Field(
        alias="weightUnit", default=None
    )
    weight_units: Optional[str] = Field(alias="weightUnits", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItems"], src_dict: Dict[str, Any]):
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
