#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
from datetime import datetime, timedelta

# ==================== 配置区 ====================
PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(PARENT_DIR, f"warehouse_summary_{datetime.now().strftime('%Y-%m-%d')}.csv")
REPORT_PATH = os.path.join(PARENT_DIR, f"EU_Larger_Items_Warehouse_Weekly_Summary_{datetime.now().strftime('%m%d')}.txt")

# 国家映射
COUNTRY_MAP = {
    'DE': ('德国', 'Germany'),
    'FR': ('法国', 'France'),
    'NL': ('荷兰', 'Netherlands'),
    'UK': ('英国', 'United Kingdom'),
}

# 周范围（本周一到周日）
today = datetime.now().date()
monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)
WEEK_RANGE_CN = f"{monday.month}月{monday.day}日 - {sunday.month}月{sunday.day}日"
WEEK_RANGE_EN = f"{monday.strftime('%B %d')} - {sunday.strftime('%B %d')}"
# ================================================

def load_data():
    if not os.path.exists(CSV_PATH):
        print(f"未找到数据文件: {CSV_PATH}")
        print("请先运行 process_merged_files.py")
        return None
    return pd.read_csv(CSV_PATH, encoding='utf-8-sig')

def main():
    print(f"正在生成周报 → {REPORT_PATH}")
    df = load_data()
    if df is None:
        return

    # 初始化汇总
    total = {'orders': 0, 'skus': 0, 'pcs': 0}
    inbound_by_country = {}
    inventory_by_country = {}
    outbound_by_country = {}

    for _, row in df.iterrows():
        country_code = row['仓库 / Warehouse']
        if country_code not in COUNTRY_MAP:
            continue

        # Inbound
        ib_orders = int(row['入库订单数 / ib_order_qty_cur']) if pd.notna(row['入库订单数 / ib_order_qty_cur']) else 0
        ib_skus = int(row['入库SKU数 / ib_sku_qty_cur']) if pd.notna(row['入库SKU数 / ib_sku_qty_cur']) else 0
        ib_pcs = int(row['入库总量 / ib_units_qty_cur']) if pd.notna(row['入库总量 / ib_units_qty_cur']) else 0

        total['orders'] += ib_orders
        total['skus'] += ib_skus
        total['pcs'] += ib_pcs

        inbound_by_country[country_code] = (ib_orders, ib_skus, ib_pcs)

        # Inventory
        inv_skus = int(row['库存SKU数 / inv_sku_qty_cur']) if pd.notna(row['库存SKU数 / inv_sku_qty_cur']) else 0
        inv_pcs = int(row['库存总量 / inv_units_qty_cur']) if pd.notna(row['库存总量 / inv_units_qty_cur']) else 0
        inventory_by_country[country_code] = (inv_skus, inv_pcs)

        # Outbound
        ob_pcs = int(row['出库总量 / ob_units_qty_cur']) if pd.notna(row['出库总量 / ob_units_qty_cur']) else 0
        outbound_by_country[country_code] = ob_pcs

    # 生成报告
    lines = []

    # 中文标题
    lines.append(f"大件仓储汇周汇总（{WEEK_RANGE_CN}）")
    lines.append("1. 入库验收")
    lines.append(f"总计: {total['orders']}单，{total['skus']}个SKU，{total['pcs']}件")
    for code, (orders, skus, pcs) in inbound_by_country.items():
        if orders > 0:
            lines.append(f"{COUNTRY_MAP[code][0]}: {orders}单，{skus}个SKU，{pcs}件")

    lines.append("2. 在库库存")
    total_inv_skus = sum(v[0] for v in inventory_by_country.values())
    total_inv_pcs = sum(v[1] for v in inventory_by_country.values())
    lines.append(f"总库存: {total_inv_skus}个SKU，{total_inv_pcs}件")
    for code, (skus, pcs) in inventory_by_country.items():
        lines.append(f"{COUNTRY_MAP[code][0]}: {skus}个SKU，{pcs}件")

    lines.append("3. 出库件数")
    total_out_pcs = sum(outbound_by_country.values())
    lines.append(f"总计: {total_out_pcs}件")
    for code, pcs in outbound_by_country.items():
        lines.append(f"{COUNTRY_MAP[code][0]}: {pcs}件")

    lines.append("4. 主要异常")
    lines.append("总计: 0件异常")
    lines.append("5. 出勤人数")
    lines.append("总人数范围: 28-34人")
    lines.append("法国: 6-9人")
    lines.append("荷兰: 7-8人")
    lines.append("德国: 9-10人")
    lines.append("英国: 6-7人")
    lines.append("平均出勤: 约31人/天")
    lines.append("")

    # 英文标题
    lines.append(f"EU Larger Items Warehouse Weekly Summary ({WEEK_RANGE_EN})")
    lines.append("1. Inbound Receiving")
    lines.append(f"Total: {total['orders']} orders, {total['skus']} SKUs, {total['pcs']:,} PCs")
    for code, (orders, skus, pcs) in inbound_by_country.items():
        if orders > 0:
            lines.append(f"{COUNTRY_MAP[code][1]}: {orders} orders, {skus} SKUs, {pcs:,} PCs")

    lines.append("2. Inventory in Stock")
    lines.append(f"Total Inventory: {total_inv_skus:,} SKUs, {total_inv_pcs:,} PCs")
    for code, (skus, pcs) in inventory_by_country.items():
        lines.append(f"{COUNTRY_MAP[code][1]}: {skus:,} SKUs, {pcs:,} PCs")

    lines.append("3. Outbound PCs")
    lines.append(f"Total: {total_out_pcs:,} PCs")
    for code, pcs in outbound_by_country.items():
        lines.append(f"{COUNTRY_MAP[code][1]}: {pcs:,} PCs")

    lines.append("4. Major Exceptions")
    lines.append("Total: 0 exceptions")
    lines.append("5. Attendance")
    lines.append("Total Personnel Range: 28-34 people")
    lines.append("France: 6-9 people")
    lines.append("Netherlands: 7-8 people")
    lines.append("Germany: 9-10 people")
    lines.append("United Kingdom: 6-7 people")
    lines.append("Average Attendance: Approx. 31 people/day")

    # 写入文件
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print("周报生成成功！")
    print(f"文件: {REPORT_PATH}")
    print("\n预览（前15行）：")
    print("\n".join(lines[:15]))
    print("...")

if __name__ == "__main__":
    main()
