#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Excel 合并脚本（跨平台）
Cross-platform Excel merger script

功能说明 Function Description:
-------------------------------------
- 自动遍历脚本所在目录下的每个子文件夹
  Automatically iterate through each subfolder in the same directory as this script.
- 从每个子文件夹中找出当天（或指定日期）的三个文件：
  Select three Excel files for today (or a given date):
    * 文件名包含 "checkPackageNumber"                  → Outbound
      Filename contains "checkPackageNumber"           → Outbound
    * 文件名包含 "acceptanceOfDataQuery"               → Inbound
      Filename contains "acceptanceOfDataQuery"        → Inbound
    * 文件名包含 "commodityInventoryInformationInquiry"→ Inventory
      Filename contains "commodityInventoryInformationInquiry" → Inventory
- 将三个表格合并为一个 Excel 工作簿，包含三个子表（sheet）。
  Merge the three files into one Excel workbook with three sheets.

日期参数支持三种方式 Date Argument Supports 3 Modes:
-------------------------------------
1. `python run_all.py --yesterday`      → 使用昨天的日期 Use yesterday’s date
2. `python run_all.py 2025-10-29`       → 使用位置参数日期 Use positional date
3. `python run_all.py --date 2025-10-29`→ 使用显式日期参数 Use explicit --date argument

额外可选参数 Additional Optional Flag:
-------------------------------------
--delete-others : 删除非目标日期或无关键词的文件
                  Delete files that are not for the target date or without the required keywords
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import pandas as pd

# ==================== 配置区 Configuration Area ====================

# 获取脚本所在目录
# Get the directory where this script is located
PARENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 是否将合并后的文件保存到原文件夹中
# Whether to save merged files back to the original folder
SAVE_TO_ORIGIN = True

# 若不保存回原文件夹，则输出到统一目录 merged_outputs
# If not saving to original folders, save to a unified directory "merged_outputs"
OUTPUT_BASE_DIR = os.path.join(PARENT_DIR, "merged_outputs")

# ===============================================================

def parse_args():
    """解析命令行参数 / Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="合并当天（或指定日期）三个 Excel 文件为一个文件 / Merge 3 Excel files for a given date into one workbook."
    )

    # 位置参数日期（可选）
    # Optional positional date argument
    parser.add_argument(
        "positional_date",
        nargs="?",
        help="可选日期参数（YYYY-MM-DD），若提供则作为目标日期 / Optional positional date as YYYY-MM-DD."
    )

    # 三种日期选项互斥
    # Mutually exclusive date options
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--yesterday",
        action="store_true",
        help="使用昨天作为日期 / Use yesterday as the target date."
    )
    group.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="使用指定日期 / Use the specific date."
    )

    # 是否删除非匹配文件
    # Whether to delete files that don’t match the target date or keywords
    parser.add_argument(
        "--delete-others",
        action="store_true",
        help="删除非目标日期或无关键词文件（旧行为） / Delete non-matching files (legacy behaviour)."
    )
    return parser.parse_args()

def coerce_date(date_str: str) -> datetime.date:
    """验证并转换日期格式 / Validate and convert a string to date format"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"日期格式错误 Invalid date '{date_str}'. 期望格式 Expected format: YYYY-MM-DD.") from e

def resolve_target_date(args) -> datetime.date:
    """确定目标日期 / Resolve which date to use"""
    if args.yesterday:
        return datetime.now().date() - timedelta(days=1)
    if args.positional_date:
        return coerce_date(args.positional_date)
    if args.date:
        return coerce_date(args.date)
    return datetime.now().date()

def main():
    """主程序入口 / Main entry point"""
    args = parse_args()
    target_date = resolve_target_date(args)
    target_str = target_date.strftime("%Y-%m-%d")

    print("\n" + "="*70)
    print(f"开始执行 - 目标日期 Target date: {target_str}")
    print(f"脚本所在目录 Parent directory: {PARENT_DIR}")
    print(f"是否保存到原文件夹 Save to original folder: {SAVE_TO_ORIGIN}")
    print(f"删除非匹配文件 Delete non-matching files: {args.delete_others}")
    if not SAVE_TO_ORIGIN:
        os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
        print(f"统一输出目录 Unified output directory: {OUTPUT_BASE_DIR}")
    print("="*70 + "\n")

    processed = 0   # 处理的文件夹数量 / Number of subfolders processed
    success = 0     # 成功合并数量 / Successfully merged folders count

    # 遍历父目录下的所有子文件夹
    # Iterate through all subfolders in the parent directory
    for item in sorted(os.listdir(PARENT_DIR)):
        folder_path = os.path.join(PARENT_DIR, item)

        # 跳过隐藏文件、系统文件夹和非目录项
        # Skip hidden files, system folders, and non-directory items
        if item.startswith('.') or item in {'warelytic', '__pycache__', 'merged_outputs'}:
            continue
        if not os.path.isdir(folder_path):
            continue

        print(f"\n处理子文件夹 Processing subfolder: {item}")
        print(f"路径 Path: {folder_path}")
        processed += 1

        # 三类文件占位符
        # Placeholder for three required Excel files
        files_to_keep = {'Outbound': None, 'Inbound': None, 'Inventory': None}

        try:
            all_files = os.listdir(folder_path)
        except Exception as e:
            print(f"无法读取目录 Cannot read folder: {e}")
            continue

        # 仅保留 Excel 文件
        # Keep only Excel files
        excel_files = [f for f in all_files if f.lower().endswith(('.xlsx', '.xls'))]
        print(f"发现 Found {len(excel_files)} 个 Excel 文件: {excel_files or '无 None'}")

        deleted = 0
        for file in excel_files:
            file_path = os.path.join(folder_path, file)
            print(f"\n检查文件 Checking file: {file}")

            # 若开启删除模式且文件名中不含目标日期 → 删除
            # If delete mode is enabled and file does not contain target date → delete it
            if args.delete_others and (target_str not in file):
                print(f"删除文件 Deleting file: 不含目标日期 Missing target date {target_str}")
                try:
                    os.remove(file_path)
                    deleted += 1
                except Exception as e:
                    print(f"删除失败 Delete failed: {e}")
                continue

            # 不含目标日期则跳过
            # Skip files that do not contain target date
            if target_str not in file:
                print(f"跳过 Skip: 不含目标日期 Missing target date {target_str}")
                continue

            # 根据关键词识别文件类型
            # Identify file type by keyword
            if 'checkPackageNumber' in file:
                files_to_keep['Outbound'] = file_path
                print("匹配 Match → Outbound")
            elif 'acceptanceOfDataQuery' in file:
                files_to_keep['Inbound'] = file_path
                print("匹配 Match → Inbound")
            elif 'commodityInventoryInformationInquiry' in file:
                files_to_keep['Inventory'] = file_path
                print("匹配 Match → Inventory")
            else:
                # 无关键词文件可选删除
                # Delete files without valid keywords (if delete mode is on)
                if args.delete_others:
                    print(f"含日期但无关键词 → 删除 Has date but no keyword → deleting")
                    try:
                        os.remove(file_path)
                        deleted += 1
                    except Exception as e:
                        print(f"删除失败 Delete failed: {e}")

        if args.delete_others:
            print(f"已删除文件数 Files deleted: {deleted}")

        # 检查是否缺少必须文件
        # Check if any required file is missing
        missing = [k for k, v in files_to_keep.items() if v is None]
        if missing:
            print(f"缺少文件 Missing files → {missing}，跳过此文件夹 Skip this folder.")
            continue

        # 读取 Excel 文件
        # Read Excel files
        dfs = {}
        for sheet_name, fpath in files_to_keep.items():
            print(f"\n读取文件 Reading {sheet_name}: {os.path.basename(fpath)}")
            try:
                df = pd.read_excel(fpath)
                print(f"读取成功 Read success: {df.shape[0]} 行 rows × {df.shape[1]} 列 cols")
                dfs[sheet_name] = df
            except Exception as e:
                print(f"读取失败 Read failed: {e}")
                dfs = {}
                break

        if not dfs:
            continue

        # 生成输出文件路径（如重名则自动编号）
        # Generate output file path (auto-increment if exists)
        output_dir = folder_path if SAVE_TO_ORIGIN else OUTPUT_BASE_DIR
        base_name = f"{item}{target_str}.xlsx"
        output_path = os.path.join(output_dir, base_name)
        if os.path.exists(output_path):
            idx = 1
            while True:
                candidate = os.path.join(output_dir, f"{item}{target_str}({idx}).xlsx")
                if not os.path.exists(candidate):
                    output_path = candidate
                    break
                idx += 1

        # 写入合并结果
        # Write merged workbook
        print(f"\n输出文件 Writing merged file: {output_path}")
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sname, df in dfs.items():
                    df.to_excel(writer, sheet_name=sname, index=False)
                    print(f"写入 sheet: {sname} ({df.shape[0]} 行 rows)")
            print("合并成功 Merge succeeded!")
            success += 1
        except Exception as e:
            print(f"合并失败 Merge failed: {e}")

    # 汇总总结
    # Summary
    print("\n" + "="*70)
    print("执行完成 Execution completed!")
    print(f"处理子文件夹 Subfolders processed: {processed}")
    print(f"成功合并 Successfully merged: {success}")
    print(f"失败或跳过 Failed or skipped: {processed - success}")
    print("="*70)

if __name__ == "__main__":
    main()
