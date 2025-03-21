import json
from typing import Optional

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Extra, Field, root_validator

from broers_langchain.wrappers import SQLDatabase


class DataHubTool(BaseModel):
    """Base tool for interacting with a SQL database."""
    db: SQLDatabase = Field(exclude=True)

    class Config(BaseTool.Config):
        pass


# def generateSql(category: str, query_number: str):
#     if category == "order":
#         sql = f"SELECT o.id,o.rd3_order_id,o.platform_reference_no,o.channel,o.order_type,o.is_manual," \
#               f"o.manual_order_no,o.date_placed,o.date_paid,o.shipping_at," \
#               f"o.order_status_txt AS order_status,o.reissue_rd3_order_id,o.reissue_platform_reference_no," \
#               f"o.is_presale,o.carrier,o.tracking,o.tracking_status,o.last_event_activity,o.last_event_at," \
#               f"o.tracking_query_url,o.is_intercept,o.intercept_type,o.on_intercept_at FROM view_orders o " \
#               f"WHERE o.rd3_order_id LIKE '%{query_number}%' OR o.platform_reference_no LIKE '%{query_number}%' OR" \
#               f" o.id LIKE '%{query_number}%' OR o.tracking LIKE '%{query_number}%' OR " \
#               f"o.manual_order_no LIKE '%{query_number}%' ORDER BY o.date_paid DESC LIMIT 10"
#     elif category == "sku":
#         sql = f"select ps.sku,s.title,s.pline,ps.purchase_sku,ps.purchase_order_no,s.stock,ps.quntity,ps.buyer_name," \
#               f"ps.handler_name from view_order_purchase_skus ps left join view_skus s on s.sku=ps.sku " \
#               f"and s.purchase_sku=ps.purchase_sku where ps.order_id like '%'{query_number}'%' or " \
#               f"ps.rd3_order_id like '%'{query_number}'%' or ps.platform_reference_no like '%'{query_number}'%' limit 20;"
#     elif category == "tracking":
#         sql = f"select t.tracking_number,t.carrier,t.warehouse_code,t.tracking_url,t.tracking_status," \
#               f"ps.purchase_sku,ps.quntity from aws_tracking t " \
#               f"left join view_order_purchase_skus ps on ps.order_id=t.order_id " \
#               f"and ps.tracking_number=t.tracking_number where t.order_id like '%'{query_number}'%'" \
#               f" or t.order_no like '%'{query_number}'%' or t.tracking_number like '%'{query_number}'%' limit 20;"
#     else:
#         sql = None
#     return sql


def queryOrderInfo(self, query_number: str):
    order_info_str = ""
    order_skus_info_str = ""
    order_tracking_info_str = ""

    # 查询订单基础信息
    # 查询订单SKU信息
    # 查询订单物流信息
    # 组合成输出模板
    order_base_sql = f"SELECT o.id,o.rd3_order_id,o.platform_reference_no,o.channel,o.order_type,o.is_manual," \
                     f"o.manual_order_no,o.date_placed,o.date_paid,o.shipping_at," \
                     f"o.order_status_txt AS order_status,o.reissue_rd3_order_id,o.reissue_platform_reference_no," \
                     f"o.is_presale,o.carrier,o.tracking,o.tracking_status,o.last_event_activity,o.last_event_at," \
                     f"o.tracking_query_url,o.is_intercept,o.intercept_type,o.on_intercept_at,o.grand_total," \
                     f"o.postage_shipping_estimated_amount FROM view_orders o " \
                     f"WHERE o.rd3_order_id LIKE '%{query_number}%' OR " \
                     f"o.platform_reference_no LIKE '%{query_number}%' OR" \
                     f" o.id LIKE '%{query_number}%' OR o.tracking LIKE '%{query_number}%' OR " \
                     f"o.manual_order_no LIKE '%{query_number}%' ORDER BY o.date_paid DESC LIMIT 1"
    order_base_result = self.db.run_no_throw(order_base_sql)
    if order_base_result is not None and order_base_result != '':
        order_info = eval(order_base_result)[0]
        if order_info is not None:
            order_info_str = f"|||||\n" \
                             f"|:---|:---|:---|:---|\n" \
                             f"|Order Id|{order_info[0]}|RD3 Order Id|{order_info[1]}|\n" \
                             f"|Platform Reference No|{order_info[2]}|Platform|{order_info[3]}|\n" \
                             f"|Order Status|{order_info[10]}|Is Presale|{order_info[13]}|\n" \
                             f"|Total Amount|{order_info[23]}|Shipping Amount|{order_info[24]}|\n"
            if order_info[20] == "Y":
                order_info_str += f"|Intercept Type|{order_info[21]}|Intercept At|{order_info[22]}|\n"
            if order_info[5] == "Y":
                order_info_str += f"|Manual Order No|{order_info[6]}|Manual RD3 Order No|{order_info[11]}|\n" \
                                  f"|Manual Platform Reference No|{order_info[12]}|||\n"
        order_id = order_info[0]
        order_timeline_sql = f"select " \
                             f"DATE_FORMAT(max(erp_create_at),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(erp_placed_at),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(erp_paid_at),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(presale_normal),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(intercept_at),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"max(intercept_reason)," \
                             f"DATE_FORMAT(max(intercept_handle_at),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(erp_push_scp),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(wms_sa_created),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(lsp_booking),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(wms_wave_print),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(pre_shipping_at),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(erp_cancel),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(lsp_cancel),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(outbound_at),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(lsp_close),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(first_scan_at),\"yyyy-MM-dd HH:mm:ss\")," \
                             f"DATE_FORMAT(max(sign_for_at),\"yyyy-MM-dd HH:mm:ss\")" \
                             f" from view_order_timeline ot where ot.id = \"{order_id}\" group by ot.id"
        order_timeline_result = self.db.run_no_throw(order_timeline_sql)
        order_time_str = "|TIME|SYSTEM|REMARK|\n|:---|:---|:---|\n"
        if order_timeline_result is not None and order_timeline_result != '':
            order_times = eval(order_timeline_result)[0]
            timeline_dict = {}
            timeline_dict[order_times[1]] = f"|{order_times[1]}|PLATFORM|PLATFORM CREATED ORDER TIME|\n"
            timeline_dict[order_times[2]] = f"|{order_times[2]}|PLATFORM|PLATFORM ORDER PAYMENT TIME|\n"
            timeline_dict[order_times[0]] = f"|{order_times[0]}|ERP|PULL ORDER TIME|\n"

            if order_times[3] is not None and order_times[3] != "":
                timeline_dict[order_times[3]] = f"|{order_times[3]}|MKT|SWITCH TO NORMAL ORDER TIME|\n"
            if order_times[4] is not None and order_times[4] != "":
                timeline_dict[order_times[4]] = f"|{order_times[4]}|ERP|INTERCEPT REASON: {order_times[5]}|\n"
            if order_times[6] is not None and order_times[6] != "":
                timeline_dict[order_times[6]] = f"|{order_times[6]}|CS|INTERCEPTION ORDER PROCESSING TIME|\n"
            if order_times[7] is not None and order_times[7] != "":
                timeline_dict[order_times[7]] = f"|{order_times[7]}|SCP|SCP RECEIVING ORDER TIME|\n"
            if order_times[8] is not None and order_times[8] != "":
                timeline_dict[order_times[8]] = f"|{order_times[8]}|WMS|WMS RECEIVING ORDER TIME|\n"
            if order_times[9] is not None and order_times[9] != "":
                timeline_dict[order_times[9]] = f"|{order_times[9]}|LSP|LSP BOOKING LABEL TIME|\n"
            if order_times[10] is not None and order_times[10] != "":
                timeline_dict[order_times[10]] = f"|{order_times[10]}|WMS|WAREHOUSE WAVE PRINTING TIME|\n"
            if order_times[11] is not None and order_times[11] != "":
                timeline_dict[
                    order_times[11]] = f"|{order_times[11]}|ERP|SYNCHRONIZE TRACKING NUMBER TO PLATFORM TIME|\n"
            if order_times[12] is not None and order_times[12] != "":
                timeline_dict[order_times[12]] = f"|{order_times[12]}|ERP|ERP CANCEL ORDER TIME|\n"
            if order_times[13] is not None and order_times[13] != "":
                timeline_dict[order_times[13]] = f"|{order_times[13]}|LSP|LSP CANCEL BOOKING TIME|\n"
            if order_times[14] is not None and order_times[14] != "":
                timeline_dict[order_times[14]] = f"|{order_times[14]}|WMS|ORDER OUTBOUND TIME|\n"
            if order_times[15] is not None and order_times[15] != "":
                timeline_dict[order_times[15]] = f"|{order_times[15]}|LSP|SUBMIT MANIFEST TIME|\n"

            sorted_timeline_keys = sorted(timeline_dict.keys())
            for key in sorted_timeline_keys:
                order_time_str += timeline_dict[key]

        order_sku_sql = f"select vs.pline,vs.sku,ops.purchase_sku,ops.quntity AS purchase_quantity," \
                        f"ops.buyer_name,ops.handler_name," \
                        f"ops.unit_price,vs.p_stock,DATE_FORMAT(vs.eta,\"yyyy-MM-dd\"),vs.inner_length,vs.inner_width,vs.inner_height," \
                        f"vs.inner_net_weight,vs.inner_volume" \
                        f" from view_order_skus os " \
                        f"LEFT JOIN view_order_purchase_skus ops ON ops.sku = os.sku and ops.order_id = os.order_id " \
                        f"LEFT JOIN view_skus vs ON vs.purchase_sku = ops.purchase_sku and vs.sku = ops.sku " \
                        f"where os.order_id = \"{order_id}\" ORDER BY ops.sku ASC,ops.purchase_sku ASC"
        order_sku_result = self.db.run_no_throw(order_sku_sql)
        if order_sku_result is not None and order_sku_result != '':
            order_skus_info_str += f"|pline|sku|purchase sku|qty|buyer|handler|price|stock|eta|length|width|height|weight|CBM|\n" \
                                   f"|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|" \
                                   f":---:|:---:|:---:|:---:|\n"

            for order_sku in eval(order_sku_result):
                order_skus_info_str += f"|{order_sku[0]}|{order_sku[1]}|{order_sku[2]}|{order_sku[3]}|{order_sku[4]}|" \
                                       f"{order_sku[5]}|{order_sku[6]}|{order_sku[7]}|{order_sku[8]}|{order_sku[9]}|" \
                                       f"{order_sku[10]}|{order_sku[11]}|{order_sku[12]}|{order_sku[13]}|\n"

        order_tracking_sql = f"SELECT t.tracking_number,t.tracking_status,t.tracking_url,t.warehouse_code," \
                             f" t.carrier, t.official_website from aws_tracking t " \
                             f"where t.order_id = \"{order_id}\" order by t.tracking_number asc"
        order_tracking_result = self.db.run_no_throw(order_tracking_sql)

        if order_tracking_result is not None and order_tracking_result != '':
            for order_tracking in eval(order_tracking_result):

                order_tracking_info_str = f"- [{order_tracking[0]}]({order_tracking[2]})\n"
                order_tracking_detail_sql = f"SELECT DATE_FORMAT(td.event_at,\"yyyy-MM-dd HH:mm:ss\"),td.event_code,td.activity from view_tracking_details td " \
                                            f"where td.tracking_number = \"{order_tracking[0]}\" order by td.event_at desc"
                order_tracking_detail_result = self.db.run_no_throw(order_tracking_detail_sql)
                order_tracking_detail_info_str = ""
                if order_tracking_detail_result is not None and order_tracking_detail_result != '':
                    order_tracking_detail_info_str = "    ||||\n    |:---|:---|:---|\n"
                    for td in eval(order_tracking_detail_result):
                        order_tracking_detail_info_str += f"    |{td[0]}|{td[1]}|{td[2]}|\n"
                    order_tracking_info_str += order_tracking_detail_info_str
        orderInfoStr = f">Order Information:\n\n{order_info_str}\n" \
                       f">Order Timeline:\n\n{order_time_str}\n" \
                       f">SKU Information:\n\n{order_skus_info_str}\n" \
                       f">Tracking Information:\n\n{order_tracking_info_str}"
        return orderInfoStr
    return None


def querySkuInfo(self, query_number: str):
    sku_sql = f"select pline,sku,purchase_sku,title,main_image," \
              f"combo_type,quantity,amazon_fba_sku,is_presell,DATE_FORMAT(presell_end_at,\"yyyy-MM-dd\")," \
              f"is_spare_part,is_packable,sale_status," \
              f"inner_length,inner_width,inner_height,inner_net_weight,inner_volume,out_length,out_width," \
              f"out_cross_weight,out_volume,buyer_name,handler_name,stock,p_stock,DATE_FORMAT(eta,\"yyyy-MM-dd\") " \
              f"from view_skus s where s.sku = \"{query_number}\" or s.purchase_sku = \"{query_number}\""
    sku_result = self.db.run_no_throw(sku_sql)
    sku_info_str = ""
    if sku_result is not None and sku_result != "":
        first_sku_item = eval(sku_result)[0]
        sale_sku = first_sku_item[1]
        purchase_sku = first_sku_item[2]
        if query_number == purchase_sku:
            # 查询结果是采购SKU
            sku_info_str = f">{purchase_sku}\n\n" \
                           f"|||||\n|:---|:---|:---|:---|\n" \
                           f"|length|{first_sku_item[13]}|width|{first_sku_item[14]}|\n" \
                           f"|height|{first_sku_item[15]}|weight|{first_sku_item[16]}|\n" \
                           f"|buyer|{first_sku_item[22]}|handler|{first_sku_item[23]}|\n" \
                           f"|inventory|{first_sku_item[25]}|eta|{first_sku_item[26]}|\n\n"
            # 查询SKU 库存信息
            inventory_sql = f"select vi.BG01,vi.BG02,vi.BG03,vi.BG05,vi.BG06,vi.BG07," \
                            f"vi.FBA,vi.TOTAL,(vi.lock_number+vi.sunyee_locked+vi.outlet_locked+vi.edrop_locked)," \
                            f"vi.transfer,vi.myself,vi.lock_number,vi.sunyee,vi.sunyee_locked," \
                            f"vi.outlet,vi.outlet_locked,vi.edrop,vi.edrop_locked " \
                            f"from oms_system_live.hpoms_view_inventory vi where vi.sku = \"{query_number}\""
            inventory_result = self.db.run_no_throw(inventory_sql)
            if inventory_result is not None and inventory_result != "":
                inventory = eval(inventory_result)[0]
                # 渠道库存分布
                c_inventory_str = "|total|lock|transfer|myself|myself lock|sunyee|sunyee lock|outlet|outlet lock|" \
                                  "edrop|edrop lock|\n " \
                                  "|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|\n"
                c_inventory_str += f"|{inventory[7]}|{inventory[8]}|{inventory[9]}|{inventory[10]}|{inventory[11]}|" \
                                   f"{inventory[12]}|{inventory[13]}|{inventory[14]}|{inventory[15]}|{inventory[16]}|" \
                                   f"{inventory[17]}|\n"
                # 仓库库存分布
                w_inventory_str = "|BG02|BG03|BG05|BG06|BG07|\n" \
                                  "|:---|:---|:---|:---|:---|\n"
                w_inventory_str += f"|{inventory[1]}|{inventory[2]}|{inventory[3]}|{inventory[4]}|{inventory[5]}|\n"
                sku_info_str += f">Inventory Detail\n\n" \
                                f"{w_inventory_str}\n\n" \
                                f"{c_inventory_str}\n\n"

            sale_table_str = "|sku|pline|combo type|fba sku|pre-sale|inventory|status|\n" \
                             "|:---|:---|:---|:---|:---|:---|:---|\n"
            for sku in eval(sku_result):
                sale_table_str += f"|{sku[1]}|{sku[0]}|{sku[5]}|{sku[7]}|{sku[8]}|{sku[24]}|{sku[12]}|\n"
            sku_info_str += ">Sales SKU LIST\n\n" + sale_table_str
            # 查询采购SKU 批次信息
            sku_asn_sql = f"select job_no,DATE_FORMAT(eta,\"yyyy-MM-dd\"),qty,cost from view_sku_asn sa" \
                          f" where sa.sku = \'{purchase_sku}\' order by DATE_FORMAT(eta,\"yyyy-MM-dd\") desc"
            asn_result = self.db.run_no_throw(sku_asn_sql)
            if asn_result is not None and asn_result != "":
                asn_info_str = "|job_no|eta|qty|cost|\n" \
                               "|:---|:---|:---|:---|\n"
                for asn in eval(asn_result):
                    asn_info_str += f'|{asn[0]}|{asn[1]}|{asn[2]}|{asn[3]}|\n'
                sku_info_str += "\n\n>ASN LIST\n\n" + asn_info_str
        else:
            # 查询结果是销售SKU
            sku_info_str = f">{sale_sku}\n\n"
            if first_sku_item[4] is not None and first_sku_item[4] != '':
                sku_info_str += f"* ![]({first_sku_item[4]})\n\n"

            sku_info_str += f"|||||\n|:---|:---|:---|:---|\n" \
                            f"|pline|{first_sku_item[0]}|title|{first_sku_item[3]}|\n" \
                            f"|type|{first_sku_item[5]}|fba sku|{first_sku_item[7]}|\n" \
                            f"|pre-sale|{first_sku_item[8]}|status|{first_sku_item[12]}|\n" \
                            f"|inventory|{first_sku_item[24]}|||\n\n"
            purchase_table_str = "|purchase sku|qty|length|width|height|weight|buyer|handler|inventory|eta|packable|\n" \
                                 "|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|\n"
            for sku in eval(sku_result):
                purchase_table_str += f"|{sku[2]}|{sku[6]}|{sku[13]}|{sku[14]}|{sku[15]}|" \
                                      f"{sku[16]}|{sku[22]}|{sku[23]}|{sku[25]}|{sku[26]}|{sku[11]}\n"
            sku_info_str += ">Purchase SKU LIST\n\n" + purchase_table_str
        return sku_info_str
    return None


def queryTrackingInfo(self, query_number: str):
    tracking_sql = f"select order_no,order_id,tracking_number,tracking_status,tracking_url," \
                   f"carrier,official_website from aws_tracking t where t.tracking_number =\"{query_number}\" limit 1"
    tracking_result = self.db.run_no_throw(tracking_sql)
    if tracking_result is not None and tracking_result != "":
        tracking = eval(tracking_result)[0]
        order_tracking_info_str = f"> [{tracking[2]}]({tracking[4]})\n" \
                                  f" * Platform Reference No: {tracking[0]}\n" \
                                  f" * Carrier: {tracking[5]}\n" \
                                  f" * Query URL: {tracking[4]}\n"
        order_tracking_detail_sql = f"SELECT DATE_FORMAT(td.event_at,\"yyyy-MM-dd HH:mm:ss\"),td.event_code," \
                                    f"td.activity from view_tracking_details td " \
                                    f"where td.tracking_number = \"{tracking[2]}\" order by td.event_at desc"
        order_tracking_detail_result = self.db.run_no_throw(order_tracking_detail_sql)
        order_tracking_detail_info_str = ""
        if order_tracking_detail_result is not None and order_tracking_detail_result != '':
            order_tracking_detail_info_str = "    ||||\n    |:---|:---|:---|\n"
            for td in eval(order_tracking_detail_result):
                order_tracking_detail_info_str += f"    |{td[0]}|{td[1]}|{td[2]}|\n"
            order_tracking_info_str += order_tracking_detail_info_str
        return order_tracking_info_str
    return None


class QueryDataHubTool(DataHubTool, BaseTool):
    """Tool for querying a SQL database."""

    name: str = "datahub_query"
    description: str = """
    Input to this tool is a json string with {{"category": "", "query_number": "" }},category value must in [
        "order","sku","tracking","auto"
    ],query_number is order number or sku number or tracking number only, output is a result markdown.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the tool_input params, check the query_number and category, and try again.
    """
    return_direct: bool = True

    def _run(
            self,
            tool_input: str,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the query, return the results or an error message."""
        empty_msg = "Sorry, no relevant information can be found. You can try asking like this:\n" \
                    "1. Query order information\n2. Query SKU information\n3. Query logistics information\n\n" \
                    "For example:\n\n" \
                    "   Order info: <your order number here>"
        category = "auto"
        query_number = None
        result = ""
        if isinstance(tool_input, str):
            tool_input = json.loads(tool_input)
        if isinstance(tool_input, dict):
            # category = tool_input["category"] if "category" in tool_input.keys() else "auto"
            query_number = tool_input["query_number"] if "query_number" in tool_input.keys() else None
            if category == "order":
                result = queryOrderInfo(self, query_number)
            elif category == "sku":
                result = querySkuInfo(self, query_number)
            elif category == "tracking":
                result = queryTrackingInfo(self, query_number)
            else:
                result = queryOrderInfo(self, query_number)
                if result is not None:
                    return result
                result = querySkuInfo(self, query_number)
                if result is not None:
                    return result
                result = queryTrackingInfo(self, query_number)
                if result is not None:
                    return result
        return empty_msg if result is None else result
