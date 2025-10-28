#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
macOS 专用 - 合并 Excel 表格（只处理当前目录的子文件夹）
"""

import os
import pandas as pd
from datetime import datetime

# ==================== 配置区 ====================
# 父目录：脚本所在目录（即当前目录）
PARENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 合并文件保存到原文件夹？True=是
SAVE_TO_ORIGIN = True

# 统一输出目录（如果 SAVE_TO_ORIGIN=False）
OUTPUT_BASE_DIR = os.path.join(PARENT_DIR, "merged_outputs")
# ================================================

def get_today_str():
    return datetime.now().strftime("%Y-%m-%d")

def main():
    today = get_today_str()
    print("\n" + "="*70)
    print(f"开始执行 - 日期: {today}")
    print(f"脚本所在目录（父目录）: {PARENT_DIR}")
    print(f"只处理此目录下的子文件夹")
    print(f"合并保存到原文件夹: {SAVE_TO_ORIGIN}")
    if not SAVE_TO_ORIGIN:
        os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
        print(f"统一输出目录: {OUTPUT_BASE_DIR}")
    print("="*70 + "\n")

    processed = 0
    success = 0

    # 遍历当前目录下的所有条目
    for item in sorted(os.listdir(PARENT_DIR)):
        folder_path = os.path.join(PARENT_DIR, item)

        # 跳过：脚本本身、虚拟环境、隐藏文件、非文件夹
        if item.startswith('.'):  # .DS_Store, .git 等
            print(f"跳过隐藏文件: {item}")
            continue
        if item in {'warelytic', '__pycache__', 'merged_outputs'}:  # 常见干扰项
            print(f"跳过系统/环境文件夹: {item}")
            continue
        if os.path.isfile(folder_path):
            print(f"跳过文件: {item}")
            continue
        if not os.path.isdir(folder_path):
            print(f"跳过非目录: {item}")
            continue

        print(f"\n处理子文件夹: {item}")
        print(f"  路径: {folder_path}")
        processed += 1

        files_to_keep = {
            'Outbound': None,
            'Inbound': None,
            'Inventory': None
        }

        # 列出 Excel 文件
        try:
            all_files = os.listdir(folder_path)
        except Exception as e:
            print(f"  无法读取目录: {e}")
            continue

        excel_files = [f for f in all_files if f.lower().endswith(('.xlsx', '.xls'))]
        print(f"  发现 {len(excel_files)} 个 Excel 文件: {excel_files or '无'}")

        deleted = 0
        for file in excel_files:
            file_path = os.path.join(folder_path, file)
            print(f"\n  检查: {file}")

            if today not in file:
                print(f"  删除: 不含日期 {today}")
                try:
                    os.remove(file_path)
                    print(f"  已删除: {file_path}")
                    deleted += 1
                except Exception as e:
                    print(f"  删除失败: {e}")
                continue

            matched = False
            if 'checkPackageNumber' in file:
                files_to_keep['Outbound'] = file_path
                print(f"  匹配 → Outbound")
                matched = True
            elif 'acceptanceOfDataQuery' in file:
                files_to_keep['Inbound'] = file_path
                print(f"  匹配 → Inbound")
                matched = True
            elif 'commodityInventoryInformationInquiry' in file:
                files_to_keep['Inventory'] = file_path
                print(f"  匹配 → Inventory")
                matched = True

            if not matched:
                print(f"  警告: 含日期但无关键词 → 删除")
                try:
                    os.remove(file_path)
                    print(f"  已删除: {file_path}")
                    deleted += 1
                except Exception as e:
                    print(f"  删除失败: {e}")

        print(f"  本文件夹删除 {deleted} 个文件")

        missing = [k for k, v in files_to_keep.items() if v is None]
        if missing:
            print(f"  失败: 缺少文件 → {missing}")
            continue

        # 读取
        dfs = {}
        for sheet_name, fpath in files_to_keep.items():
            print(f"\n  读取 {sheet_name}: {os.path.basename(fpath)}")
            try:
                df = pd.read_excel(fpath)
                print(f"  成功: {df.shape[0]} 行 × {df.shape[1]} 列")
                dfs[sheet_name] = df
            except Exception as e:
                print(f"  读取失败: {e}")
                break
        else:
            output_name = f"{item}{today}.xlsx"
            output_path = os.path.join(folder_path, output_name) if SAVE_TO_ORIGIN else os.path.join(OUTPUT_BASE_DIR, output_name)
            print(f"\n  合并输出: {output_path}")

            try:
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    for sname, df in dfs.items():
                        df.to_excel(writer, sheet_name=sname, index=False)
                        print(f"  写入 sheet: {sname} ({df.shape[0]} 行)")
                print(f"  合并成功！")
                success += 1
            except Exception as e:
                print(f"  合并失败: {e}")

    # 总结
    print("\n" + "="*70)
    print(f"执行完成！")
    print(f"处理子文件夹: {processed} 个")
    print(f"成功合并: {success} 个")
    print(f"失败/跳过: {processed - success} 个")
    print("="*70)

if __name__ == "__main__":
    main()
