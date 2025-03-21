#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
单个Excel文件处理示例
"""

import os
import sys

# 添加父目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from oect_excel_processor import ExcelProcessor


def main():
    """
    展示如何处理单个Excel文件
    """
    # 获取示例文件路径
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        # 使用当前目录中的第一个.xls文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        xls_files = [f for f in os.listdir(current_dir) if f.endswith('.xls')]
        
        if not xls_files:
            print("当前目录中未找到任何Excel文件，请提供文件路径作为参数")
            return 1
        
        excel_file = os.path.join(current_dir, xls_files[0])
    
    print(f"处理Excel文件: {excel_file}")
    
    # 创建处理器实例
    sheet_types = ["transfer", "transient"]
    output_prefix = "example_output"
    
    processor = ExcelProcessor(excel_file, sheet_types, output_prefix)
    
    # 获取工作表信息
    sheet_info = processor.get_sheet_info()
    
    print("工作表信息:")
    for sheet_name, sheet_type in sheet_info.items():
        print(f"- {sheet_name}: {sheet_type}")
    
    # 处理并保存
    saved_files = processor.process_and_save()
    
    print("\n处理完成，生成的CSV文件:")
    for file in saved_files:
        print(f"- {file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 