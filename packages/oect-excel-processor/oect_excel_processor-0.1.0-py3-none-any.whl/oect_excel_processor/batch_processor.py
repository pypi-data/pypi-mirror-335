import os
import glob
from typing import List, Dict, Optional, Union, Tuple, Callable
import pandas as pd
from natsort import natsorted
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
import traceback

from .excel_processor import ExcelProcessor


class BatchExcelProcessor:
    """
    批量处理Excel文件的类
    提供批量处理功能
    """
    
    def __init__(self, directory: str, file_pattern: str = "*.xls", 
                 sheet_types: List[str] = None, output_prefix: str = "batch_output"):
        """
        初始化BatchExcelProcessor类
        
        Args:
            directory: 包含Excel文件的目录路径
            file_pattern: 文件匹配模式，默认为"*.xls"
            sheet_types: 工作表类型列表，每个元素为'transfer'或'transient'
            output_prefix: 输出CSV文件的前缀名
        """
        self.directory = directory
        self.file_pattern = file_pattern
        self.sheet_types = sheet_types if sheet_types else ["transfer"]
        self.output_prefix = output_prefix
        self._validate_inputs()
        
    @classmethod
    def create(cls, directory: str, file_pattern: str = "*.xls", 
               sheet_types: List[str] = None, output_prefix: str = "batch_output") -> 'BatchExcelProcessor':
        """
        类方法创建BatchExcelProcessor实例
        
        Args:
            directory: 包含Excel文件的目录路径
            file_pattern: 文件匹配模式，默认为"*.xls"
            sheet_types: 工作表类型列表，每个元素为'transfer'或'transient'
            output_prefix: 输出CSV文件的前缀名
            
        Returns:
            BatchExcelProcessor实例
        """
        return cls(directory, file_pattern, sheet_types, output_prefix)
    
    def _validate_inputs(self) -> None:
        """验证输入参数的有效性"""
        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"目录不存在: {self.directory}")
        
        if not os.path.isdir(self.directory):
            raise NotADirectoryError(f"指定的路径不是目录: {self.directory}")
        
        if self.sheet_types:
            for sheet_type in self.sheet_types:
                if sheet_type not in ['transfer', 'transient']:
                    raise ValueError(f"工作表类型必须是 'transfer' 或 'transient'，而不是 {sheet_type}")
    
    def get_excel_files(self) -> List[str]:
        """
        获取目录中符合模式的所有Excel文件，并按自然排序排序
        
        Returns:
            排序后的Excel文件路径列表
        """
        # 获取所有匹配的文件
        file_pattern_path = os.path.join(self.directory, self.file_pattern)
        excel_files = glob.glob(file_pattern_path)
        
        # 使用natsort包进行自然排序
        excel_files = natsorted(excel_files)
        
        return excel_files
    
    def _process_single_file(self, args: Tuple) -> Tuple[str, List[str], Optional[str]]:
        """
        处理单个Excel文件（用于多进程处理）
        
        Args:
            args: 包含处理参数的元组 (excel_file, file_index, total_files, output_dir)
            
        Returns:
            包含处理结果的元组 (excel_file, csv_files, error_message)
        """
        excel_file, file_index, total_files, output_dir = args
        file_name = os.path.basename(excel_file)
        
        print(f"处理文件 {file_index}/{total_files}: {file_name}")
        
        try:
            # 为每个工作表创建自定义前缀
            def custom_prefix_generator(sheet_index, sheet_type):
                """为每个工作表生成自定义前缀"""
                prefix = f"{self.output_prefix}-{file_index}-{sheet_index}-{sheet_type}"
                if output_dir:
                    prefix = os.path.join(output_dir, prefix)
                return prefix
            
            # 读取Excel文件
            excel_data = pd.ExcelFile(excel_file)
            all_sheets = excel_data.sheet_names
            
            # 确保工作表类型列表长度与工作表数量匹配
            sheet_types = self.sheet_types.copy()
            if len(sheet_types) < len(all_sheets):
                sheet_types.extend(['transfer'] * (len(all_sheets) - len(sheet_types)))
            elif len(sheet_types) > len(all_sheets):
                sheet_types = sheet_types[:len(all_sheets)]
            
            # 存储此文件生成的所有CSV文件
            file_csv_outputs = []
            
            # 处理每个工作表
            for j, (sheet_name, sheet_type) in enumerate(zip(all_sheets, sheet_types)):
                # 读取工作表数据
                sheet_data = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                
                # 根据工作表类型处理数据
                if sheet_type == 'transfer':
                    processor = ExcelProcessor(excel_file, [sheet_type], self.output_prefix)
                    processed_data = processor._process_transfer_sheet(sheet_data)
                else:  # transient
                    processor = ExcelProcessor(excel_file, [sheet_type], self.output_prefix)
                    processed_data = processor._process_transient_sheet(sheet_data)
                
                # 保存为CSV，使用新的命名格式
                sheet_index = j + 1
                output_file = f"{custom_prefix_generator(sheet_index, sheet_type)}.csv"
                processed_data.to_csv(output_file, index=False)
                file_csv_outputs.append(output_file)
            
            print(f"  成功处理文件: {file_name}")
            print(f"  生成的CSV文件: {len(file_csv_outputs)}")
            
            return excel_file, file_csv_outputs, None
            
        except Exception as e:
            error_message = f"处理文件 {file_name} 时出错: {str(e)}\n{traceback.format_exc()}"
            print(f"  {error_message}")
            return excel_file, [], error_message
    
    def process_all_files(self, output_dir: Optional[str] = None, use_multiprocessing: bool = False, 
                          max_workers: Optional[int] = None) -> Dict[str, List[str]]:
        """
        处理所有Excel文件
        
        Args:
            output_dir: 输出目录，如果不指定则使用当前目录
            use_multiprocessing: 是否使用多进程处理，默认为False
            max_workers: 最大工作进程数，默认为None（使用CPU核心数）
            
        Returns:
            每个Excel文件及其生成的CSV文件路径的字典
        """
        # 获取所有Excel文件
        excel_files = self.get_excel_files()
        
        if not excel_files:
            print(f"在目录 {self.directory} 中未找到匹配 {self.file_pattern} 的Excel文件")
            return {}
        
        # 创建输出目录（如果指定）
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 存储处理结果
        results = {}
        
        # 如果使用多进程处理
        if use_multiprocessing:
            # 确定工作进程数
            if max_workers is None:
                max_workers = multiprocessing.cpu_count()
            
            print(f"使用多进程处理，工作进程数: {max_workers}")
            
            # 准备处理参数
            process_args = [
                (excel_file, i + 1, len(excel_files), output_dir) 
                for i, excel_file in enumerate(excel_files)
            ]
            
            # 使用进程池执行处理任务
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_file = {
                    executor.submit(self._process_single_file, args): args[0]
                    for args in process_args
                }
                
                # 收集结果
                for future in as_completed(future_to_file):
                    excel_file, csv_files, error = future.result()
                    results[excel_file] = csv_files
        
        # 使用单进程处理（原有逻辑）
        else:
            # 处理每个Excel文件
            for i, excel_file in enumerate(excel_files):
                file_name = os.path.basename(excel_file)
                file_index = i + 1
                
                print(f"处理文件 {file_index}/{len(excel_files)}: {file_name}")
                
                try:
                    # 为每个工作表创建自定义前缀
                    def custom_prefix_generator(sheet_index, sheet_type):
                        """为每个工作表生成自定义前缀"""
                        prefix = f"{self.output_prefix}-{file_index}-{sheet_index}-{sheet_type}"
                        if output_dir:
                            prefix = os.path.join(output_dir, prefix)
                        return prefix
                    
                    # 读取Excel文件
                    excel_data = pd.ExcelFile(excel_file)
                    all_sheets = excel_data.sheet_names
                    
                    # 确保工作表类型列表长度与工作表数量匹配
                    sheet_types = self.sheet_types.copy()
                    if len(sheet_types) < len(all_sheets):
                        sheet_types.extend(['transfer'] * (len(all_sheets) - len(sheet_types)))
                    elif len(sheet_types) > len(all_sheets):
                        sheet_types = sheet_types[:len(all_sheets)]
                    
                    # 存储此文件生成的所有CSV文件
                    file_csv_outputs = []
                    
                    # 处理每个工作表
                    for j, (sheet_name, sheet_type) in enumerate(zip(all_sheets, sheet_types)):
                        # 读取工作表数据
                        sheet_data = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                        
                        # 根据工作表类型处理数据
                        if sheet_type == 'transfer':
                            processor = ExcelProcessor(excel_file, [sheet_type], self.output_prefix)
                            processed_data = processor._process_transfer_sheet(sheet_data)
                        else:  # transient
                            processor = ExcelProcessor(excel_file, [sheet_type], self.output_prefix)
                            processed_data = processor._process_transient_sheet(sheet_data)
                        
                        # 保存为CSV，使用新的命名格式
                        sheet_index = j + 1
                        output_file = f"{custom_prefix_generator(sheet_index, sheet_type)}.csv"
                        processed_data.to_csv(output_file, index=False)
                        file_csv_outputs.append(output_file)
                    
                    # 存储结果
                    results[excel_file] = file_csv_outputs
                    
                    print(f"  成功处理文件: {file_name}")
                    print(f"  生成的CSV文件: {len(file_csv_outputs)}")
                except Exception as e:
                    print(f"  处理文件 {file_name} 时出错: {str(e)}")
                    results[excel_file] = []
        
        return results
    
    def get_processing_summary(self, results: Dict[str, List[str]]) -> Dict[str, int]:
        """
        获取处理结果的摘要
        
        Args:
            results: 处理结果字典
            
        Returns:
            包含处理摘要的字典
        """
        total_files = len(results)
        successful_files = sum(1 for files in results.values() if files)
        failed_files = total_files - successful_files
        total_csv_files = sum(len(files) for files in results.values())
        
        return {
            "total_excel_files": total_files,
            "successful_files": successful_files,
            "failed_files": failed_files,
            "total_csv_files": total_csv_files
        } 