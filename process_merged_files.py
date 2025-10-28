#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import numpy as np
import sys
from datetime import datetime, timedelta


# -------------------- 日期参数处理 --------------------
def resolve_today(argv):
    """返回要使用的日期字符串（YYYY-MM-DD）。
    支持：无参数=今天；--yesterday=昨天；显式日期=YYYY-MM-DD。"""
    base = datetime.now()
    today_str = base.strftime("%Y-%m-%d")

    # 无参数 → 用今天
    if len(argv) < 2:
        return today_str

    # 显式 --yesterday
    if "--yesterday" in argv:
        return (base - timedelta(days=1)).strftime("%Y-%m-%d")

    # 尝试识别最后一个参数是日期
    arg = argv[-1]
    if arg.replace("-", "").isdigit() and len(arg) == 10:
        # 简单校验：YYYY-MM-DD
        try:
            datetime.strptime(arg, "%Y-%m-%d")
            return arg
        except ValueError:
            pass

    # 也可支持 --date 2025-10-27 的写法
    if "--date" in argv:
        try:
            idx = argv.index("--date")
            if idx + 1 < len(argv):
                cand = argv[idx + 1]
                datetime.strptime(cand, "%Y-%m-%d")
                return cand
        except Exception:
            pass

    return today_str
    
PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
TODAY = resolve_today(sys.argv)

def find_merged_files():
    merged_files = []
    for root, dirs, files in os.walk(PARENT_DIR):
        if root == PARENT_DIR:
            continue
        for file in files:
            if file.lower().endswith('.xlsx') and TODAY in file and file.startswith(os.path.basename(root)):
                file_path = os.path.join(root, file)
                merged_files.append((file, file_path, os.path.basename(root)))
    return merged_files

def main():
    print("\n" + "="*80)
    print("用法示例：python process_merged_files.py [YYYY-MM-DD] 或 --yesterday 或 --date YYYY-MM-DD")
    print(f"开始数据处理 - 日期: {TODAY}")
    print(f"搜索目录: {PARENT_DIR}")
    print("="*80 + "\n")

    merged_files = find_merged_files()
    if not merged_files:
        print("未找到统合文件！请先运行 combine_excel_sheets.py")
        return

    print(f"发现 {len(merged_files)} 个统合文件：")
    for name, path, folder in merged_files:
        print(f"  → {folder}/{name}")

    results = []
    for filename, filepath, folder_name in merged_files:
        print(f"\n{'-'*60}")
        print(f"处理: {folder_name}/{filename}")
        try:
            xls = pd.ExcelFile(filepath)

            # Initiailise
            inv_sku = inv_qty = ib_order = ib_sku = ib_qty = ob_order = ob_qty = np.nan
            inv_total_volume_m3 = np.nan  # Debug for qty_serious not defined

            # ==================== Inventory ====================
            if 'Inventory' in xls.sheet_names:
                df = pd.read_excel(xls, 'Inventory')
                cols = df.columns.str.strip()
                print(f"\n[DEBUG] Inventory 原始列名 ({len(cols)} 列):")
                for i, c in enumerate(cols, 1):
                    print(f"  {i:2d}. '{c}'")

                # --- 1. Match SKU Column ---
                sku_keywords = ['JD SKU', '商品条码']
                print(f"\n[DEBUG] 尝试匹配 SKU 列，关键词: {sku_keywords}")
                sku_col = None
                for kw in sku_keywords:
                    matches = [c for c in cols if kw in c]
                    print(f"  - 关键词 '{kw}' 匹配到: {matches}")
                    if matches:
                        sku_col = matches[0]      # 取第一个匹配
                        break

                if sku_col:
                    print(f"[DEBUG] 选中 SKU 列: '{sku_col}'")
                    data = df[sku_col].iloc[0:]          # 跳过第1行表头，但是Panda自动处理了，所以还是0
                    print(f"[DEBUG] 跳过表头后行数: {len(data)}")
                    clean = data.dropna()
                    print(f"[DEBUG] dropna() 后非空值: {len(clean)}")
                    inv_sku = clean.nunique()
                    print(f"[DEBUG] inv_sku_qty_cur = nunique() = {inv_sku}")
                else:
                    print("[WARN] 未找到任何 SKU 列 → inv_sku_qty_cur = NaN")

                # --- 2. 匹配库存量列 ---
                qty_keywords = ['库存量', 'Inventory QTY.']
                print(f"\n[DEBUG] 尝试匹配库存量列，关键词: {qty_keywords}")
                qty_col = None
                for kw in qty_keywords:
                    matches = [c for c in cols if kw in c]
                    print(f"  - 关键词 '{kw}' 匹配到: {matches}")
                    if matches:
                        qty_col = matches[0]
                        break

                if qty_col:
                    print(f"[DEBUG] 选中库存量列: '{qty_col}'")
                    data = df[qty_col].iloc[0:] # Try to skip line 0, found that pandas did that for me already
                    numeric = pd.to_numeric(data, errors='coerce')
                    print(f"[DEBUG] 转换为数值后非 NaN 数量: {numeric.notna().sum()}")
                    inv_qty = numeric.sum()
                    print(f"[DEBUG] inv_units_qty_cur = sum() = {inv_qty}")
                else:
                    print("[WARN] 未找到库存量列 → inv_units_qty_cur = NaN")
                    
                # --- 3) 维度列匹配并计算总体积（m³）---
                len_keywords = ['长', 'Length']
                wid_keywords = ['宽', 'Width']
                hei_keywords = ['高', 'Height']

                def pick_col(keywords):
                    for kw in keywords:
                        cand = [c for c in cols if kw in c]
                        if cand:
                            return cand[0], cand
                    return None, []

                L_col, L_cands = pick_col(len_keywords)
                W_col, W_cands = pick_col(wid_keywords)
                H_col, H_cands = pick_col(hei_keywords)

                print(f"\n[DEBUG] 维度列匹配：")
                print(f"  - 长/Length 候选: {L_cands} → 选用: {repr(L_col)}")
                print(f"  - 宽/Width  候选: {W_cands} → 选用: {repr(W_col)}")
                print(f"  - 高/Height 候选: {H_cands} → 选用: {repr(H_col)}")

                inv_total_volume_m3 = np.nan

                # ✅ 不再检查 qty_series，直接复用 qty_col
                if all([L_col, W_col, H_col, qty_col]):
                    L = pd.to_numeric(df[L_col], errors='coerce').fillna(0)
                    W = pd.to_numeric(df[W_col], errors='coerce').fillna(0)
                    H = pd.to_numeric(df[H_col], errors='coerce').fillna(0)
                    Q = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)

                    per_unit_m3 = (L * W * H) / 1_000_000  # mm³ → m³
                    inv_total_volume_m3 = float((per_unit_m3 * Q).sum())

                    print(f"[DEBUG] 体积计算行数: {len(df)}")
                    print(f"[DEBUG] 非零 per_unit_m3 行数: {(per_unit_m3 > 0).sum()}")
                    print(f"[DEBUG] 非零 Q 行数: {(Q > 0).sum()}")
                    print(f"[DEBUG] 在库总体积(m³) 合计: {inv_total_volume_m3:.6f}")
                else:
                    print("[WARN] 无法计算体积，缺少列 → inv_total_volume_m3 = NaN")

            # ==================== Inbound / Outbound (保持不变) ====================
            # （为了节省篇幅，这里省略，保持原逻辑不变）
            # 如需同样加 debug，可复制上面的结构

            # === Inbound ===
            if 'Inbound' in xls.sheet_names:
                df = pd.read_excel(xls, 'Inbound')
                cols = df.columns.str.strip()
                order_col = next((c for c in cols if any(kw in c for kw in ['客户入库单号', 'JD Inbound NO.'])), None)
                sku_col   = next((c for c in cols if any(kw in c for kw in ['商品编码', 'Goods NO.'])), None)
                qty_col   = next((c for c in cols if any(kw in c for kw in ['验收量', 'Receiving QTY.'])), None)
                if order_col: ib_order = df[order_col].iloc[0:].dropna().nunique()
                if sku_col:   ib_sku   = df[sku_col].iloc[0:].dropna().nunique()
                if qty_col:   ib_qty   = pd.to_numeric(df[qty_col].iloc[0:], errors='coerce').sum()

            # === Outbound ===
            if 'Outbound' in xls.sheet_names:
                df = pd.read_excel(xls, 'Outbound')
                cols = df.columns.str.strip()
                order_col = next((c for c in cols if any(kw in c for kw in ['订单号', 'JD Outbound NO.', '出库单号'])), None)
                qty_col   = next((c for c in cols if any(kw in c for kw in ['复核数量', 'Rechecked QTY', 'QTY'])), None)
                if order_col: ob_order = df[order_col].iloc[1:].dropna().nunique()
                if qty_col:   ob_qty   = pd.to_numeric(df[qty_col].iloc[1:], errors='coerce').sum()

            # ==================== 记录结果 ====================
            results.append({
                '仓库 / Warehouse': folder_name,
                '文件 / File': filename,
                '库存SKU数 / inv_sku_qty_cur': inv_sku,
                '库存总量 / inv_units_qty_cur': inv_qty,
                '入库订单数 / ib_order_qty_cur': ib_order,
                '入库SKU数 / ib_sku_qty_cur': ib_sku,
                '入库总量 / ib_units_qty_cur': ib_qty,
                '出库订单数 / ob_order_qty_cur': ob_order,
                '出库总量 / ob_units_qty_cur': ob_qty,
                '在库总体积(m³ CBM) / inv_total_volume_m3': inv_total_volume_m3,
            })

        except Exception as e:
            print(f"  处理失败: {e}")

    # ==================== 输出 ====================
    if results:
        df_out = pd.DataFrame(results)
        print("\n" + "="*80)
        print("数据处理完成！")
        print("="*80)
        print(df_out.to_string(index=False, float_format='%.0f'))

        csv_path = os.path.join(PARENT_DIR, f"warehouse_summary_{TODAY}.csv")
        df_out.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n已保存汇总文件: {csv_path}")
        print("="*80)

if __name__ == "__main__":
    main()
