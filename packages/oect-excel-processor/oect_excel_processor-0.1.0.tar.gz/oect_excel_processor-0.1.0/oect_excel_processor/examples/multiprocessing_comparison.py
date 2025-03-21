#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
多核处理与单核处理对比示例
"""

import os
import sys
import time

# 添加父目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from oect_excel_processor import BatchExcelProcessor


def main():
    """
    展示多核处理与单核处理的对比
    """
    # 获取示例目录路径
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        # 使用当前目录
        directory = os.path.dirname(os.path.abspath(__file__))
    
    # 创建输出目录
    single_output_dir = os.path.join(directory, "single_core_output")
    multi_output_dir = os.path.join(directory, "multi_core_output")
    
    for output_dir in [single_output_dir, multi_output_dir]:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    print("多核处理与单核处理对比示例")
    print("=" * 50)
    
    # 创建批处理器实例
    batch_processor = BatchExcelProcessor(
        directory=directory,
        file_pattern="*.xls",
        sheet_types=["transfer", "transient"],
        output_prefix="comparison_example"
    )
    
    # 获取Excel文件列表
    excel_files = batch_processor.get_excel_files()
    print(f"找到 {len(excel_files)} 个Excel文件")
    
    if not excel_files:
        print("未找到Excel文件，请确保目录中有.xls文件")
        return 1
    
    # 1. 使用单核处理
    print("\n1. 使用单核处理")
    start_time = time.time()
    
    results_single = batch_processor.process_all_files(
        output_dir=single_output_dir,
        use_multiprocessing=False
    )
    
    single_time = time.time() - start_time
    summary_single = batch_processor.get_processing_summary(results_single)
    
    print(f"单核处理完成，耗时: {single_time:.2f} 秒")
    print(f"处理的Excel文件数: {summary_single['total_excel_files']}")
    print(f"成功处理的文件数: {summary_single['successful_files']}")
    print(f"生成的CSV文件总数: {summary_single['total_csv_files']}")
    
    # 2. 使用多核处理
    print("\n2. 使用多核处理")
    start_time = time.time()
    
    results_multi = batch_processor.process_all_files(
        output_dir=multi_output_dir,
        use_multiprocessing=True,
        max_workers=None  # 自动使用所有可用CPU核心
    )
    
    multi_time = time.time() - start_time
    summary_multi = batch_processor.get_processing_summary(results_multi)
    
    print(f"多核处理完成，耗时: {multi_time:.2f} 秒")
    print(f"处理的Excel文件数: {summary_multi['total_excel_files']}")
    print(f"成功处理的文件数: {summary_multi['successful_files']}")
    print(f"生成的CSV文件总数: {summary_multi['total_csv_files']}")
    
    # 性能对比
    if single_time > 0:
        speedup = single_time / multi_time
        print(f"\n性能对比: 多核处理比单核处理快 {speedup:.2f} 倍")
    
    print("\n处理结果已保存到以下目录:")
    print(f"- 单核处理结果: {single_output_dir}")
    print(f"- 多核处理结果: {multi_output_dir}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 