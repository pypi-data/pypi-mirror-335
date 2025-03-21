#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
命令行接口，提供命令行工具功能
"""

import os
import sys
import argparse
from typing import List, Optional

from .excel_processor import ExcelProcessor
from .batch_processor import BatchExcelProcessor


def process_single_file(args) -> None:
    """
    处理单个Excel文件
    
    Args:
        args: 命令行参数
    """
    print(f"处理Excel文件: {args.file}")
    
    processor = ExcelProcessor(
        file_path=args.file,
        sheet_types=args.sheet_types.split(','),
        output_prefix=args.output_prefix
    )
    
    saved_files = processor.process_and_save()
    
    print(f"成功处理Excel文件: {args.file}")
    print(f"生成的CSV文件:")
    for file in saved_files:
        print(f"  - {file}")


def process_batch_files(args) -> None:
    """
    批量处理Excel文件
    
    Args:
        args: 命令行参数
    """
    print(f"批量处理目录: {args.directory}")
    print(f"文件匹配模式: {args.pattern}")
    
    # 创建输出目录（如果指定）
    if args.output_dir and not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    processor = BatchExcelProcessor(
        directory=args.directory,
        file_pattern=args.pattern,
        sheet_types=args.sheet_types.split(','),
        output_prefix=args.output_prefix
    )
    
    # 获取Excel文件列表
    excel_files = processor.get_excel_files()
    print(f"找到 {len(excel_files)} 个Excel文件")
    
    if not excel_files:
        print("未找到Excel文件，请确保目录中有匹配的文件")
        return
    
    # 处理所有文件
    results = processor.process_all_files(
        output_dir=args.output_dir,
        use_multiprocessing=args.multiprocessing,
        max_workers=args.workers
    )
    
    # 获取处理摘要
    summary = processor.get_processing_summary(results)
    
    print("\n处理摘要:")
    print(f"总Excel文件数: {summary['total_excel_files']}")
    print(f"成功处理的文件数: {summary['successful_files']}")
    print(f"处理失败的文件数: {summary['failed_files']}")
    print(f"生成的CSV文件总数: {summary['total_csv_files']}")
    
    if args.output_dir:
        print(f"\n所有CSV文件已保存到目录: {args.output_dir}")


def main(args: Optional[List[str]] = None) -> int:
    """
    主函数，处理命令行参数并执行相应操作
    
    Args:
        args: 命令行参数列表，默认为None（使用sys.argv）
        
    Returns:
        退出码
    """
    parser = argparse.ArgumentParser(
        description='OECT Excel Processor - 处理OECT性能测试后的Excel数据并转换为CSV格式'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 单文件处理子命令
    single_parser = subparsers.add_parser('single', help='处理单个Excel文件')
    single_parser.add_argument('file', help='Excel文件路径')
    single_parser.add_argument(
        '--sheet-types', '-t', 
        default='transfer,transient',
        help='工作表类型列表，以逗号分隔，例如: transfer,transient,transfer'
    )
    single_parser.add_argument(
        '--output-prefix', '-o',
        default='output',
        help='输出CSV文件的前缀名'
    )
    
    # 批量处理子命令
    batch_parser = subparsers.add_parser('batch', help='批量处理Excel文件')
    batch_parser.add_argument('directory', help='包含Excel文件的目录路径')
    batch_parser.add_argument(
        '--pattern', '-p',
        default='*.xls',
        help='文件匹配模式，默认为"*.xls"'
    )
    batch_parser.add_argument(
        '--sheet-types', '-t',
        default='transfer,transient',
        help='工作表类型列表，以逗号分隔，例如: transfer,transient,transfer'
    )
    batch_parser.add_argument(
        '--output-prefix', '-o',
        default='batch_output',
        help='输出CSV文件的前缀名'
    )
    batch_parser.add_argument(
        '--output-dir', '-d',
        help='输出目录，如果不指定则使用当前目录'
    )
    batch_parser.add_argument(
        '--multiprocessing', '-m',
        action='store_true',
        help='是否使用多进程处理'
    )
    batch_parser.add_argument(
        '--workers', '-w',
        type=int,
        default=None,
        help='最大工作进程数，默认为None（使用所有可用CPU核心）'
    )
    
    # 解析命令行参数
    parsed_args = parser.parse_args(args)
    
    # 执行相应的命令
    if parsed_args.command == 'single':
        process_single_file(parsed_args)
    elif parsed_args.command == 'batch':
        process_batch_files(parsed_args)
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main()) 