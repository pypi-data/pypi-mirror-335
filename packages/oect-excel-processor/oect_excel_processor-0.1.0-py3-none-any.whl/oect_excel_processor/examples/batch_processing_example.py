#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量处理Excel文件示例
"""

import os
import sys
import time

# 添加父目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from oect_excel_processor import BatchExcelProcessor


def main():
    """
    展示如何批量处理Excel文件
    """
    # 获取示例目录路径
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        # 使用当前目录
        directory = os.path.dirname(os.path.abspath(__file__))
    
    # 创建输出目录
    output_dir = os.path.join(directory, "batch_output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"批量处理目录: {directory}")
    
    # 创建批处理器实例
    batch_processor = BatchExcelProcessor(
        directory=directory,
        file_pattern="*.xls",
        sheet_types=["transfer", "transient"],
        output_prefix="batch_example"
    )
    
    # 获取Excel文件列表
    excel_files = batch_processor.get_excel_files()
    print(f"找到 {len(excel_files)} 个Excel文件")
    
    if not excel_files:
        print("未找到Excel文件，请确保目录中有.xls文件")
        return 1
    
    # 使用多核处理
    print("\n使用多核处理")
    start_time = time.time()
    
    results = batch_processor.process_all_files(
        output_dir=output_dir,
        use_multiprocessing=True,
        max_workers=None  # 自动使用所有可用CPU核心
    )
    
    process_time = time.time() - start_time
    summary = batch_processor.get_processing_summary(results)
    
    print(f"处理完成，耗时: {process_time:.2f} 秒")
    print(f"处理的Excel文件数: {summary['total_excel_files']}")
    print(f"成功处理的文件数: {summary['successful_files']}")
    print(f"处理失败的文件数: {summary['failed_files']}")
    print(f"生成的CSV文件总数: {summary['total_csv_files']}")
    
    print(f"\n处理结果已保存到目录: {output_dir}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 