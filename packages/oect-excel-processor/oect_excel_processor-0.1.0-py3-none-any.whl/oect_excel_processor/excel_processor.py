import os
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Dict, Union


class ExcelProcessor:
    """
    处理Excel文件并转换为CSV格式的类。
    支持两种类型的工作表处理：
    1. transfer类型：从第三行开始有字段名，共四列数据
    2. transient类型：第三行前两列是字段名，数据按每两列一组排列，需要合并
    """

    def __init__(self, file_path: str, sheet_types: List[str], output_prefix: str = "output"):
        """
        初始化ExcelProcessor类
        
        Args:
            file_path: Excel文件路径
            sheet_types: 工作表类型列表，每个元素为'transfer'或'transient'
            output_prefix: 输出CSV文件的前缀名
        """
        self.file_path = file_path
        self.sheet_types = sheet_types
        self.output_prefix = output_prefix
        self._validate_inputs()
        
    @classmethod
    def create(cls, file_path: str, sheet_types: List[str], output_prefix: str = "output") -> 'ExcelProcessor':
        """
        类方法创建ExcelProcessor实例
        
        Args:
            file_path: Excel文件路径
            sheet_types: 工作表类型列表，每个元素为'transfer'或'transient'
            output_prefix: 输出CSV文件的前缀名
            
        Returns:
            ExcelProcessor实例
        """
        return cls(file_path, sheet_types, output_prefix)
    
    def _validate_inputs(self) -> None:
        """验证输入参数的有效性"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"文件不存在: {self.file_path}")
        
        if not self.file_path.endswith(('.xls', '.xlsx')):
            raise ValueError(f"文件必须是Excel格式 (.xls 或 .xlsx): {self.file_path}")
        
        for sheet_type in self.sheet_types:
            if sheet_type not in ['transfer', 'transient']:
                raise ValueError(f"工作表类型必须是 'transfer' 或 'transient'，而不是 {sheet_type}")
    
    def _process_transfer_sheet(self, sheet_data: pd.DataFrame) -> pd.DataFrame:
        """
        处理transfer类型的工作表
        
        Args:
            sheet_data: 工作表数据
            
        Returns:
            处理后的DataFrame
        """
        # 从第三行开始，第三行是字段名
        headers = sheet_data.iloc[2].values[:4]  # 取前四列作为字段名
        data = sheet_data.iloc[3:, :4].copy()    # 取第四行开始的数据，前四列
        
        # 设置列名
        data.columns = headers
        
        return data
    
    def _process_transient_sheet(self, sheet_data: pd.DataFrame) -> pd.DataFrame:
        """
        处理transient类型的工作表
        
        Args:
            sheet_data: 工作表数据
            
        Returns:
            处理后的DataFrame
        """
        # 获取第三行前两列作为字段名
        headers = sheet_data.iloc[2, :2].values
        
        # 初始化结果DataFrame
        result_data = []
        
        # 处理所有数据列，每两列一组
        for col_idx in range(0, sheet_data.shape[1], 2):
            if col_idx + 1 >= sheet_data.shape[1]:
                break  # 确保有成对的列
                
            # 获取当前两列的数据（从第四行开始）
            col_data = sheet_data.iloc[3:, col_idx:col_idx+2].copy()
            
            # 跳过空列
            if col_data.empty or col_data.isna().all().all():
                continue
                
            # 设置列名并添加到结果中
            col_data.columns = headers
            
            # 去除全为NaN的行
            col_data = col_data.dropna(how='all')
            
            # 只保留两列都有值的行
            col_data = col_data.dropna(how='any')
            
            if not col_data.empty:
                result_data.append(col_data)
        
        # 合并所有数据
        if not result_data:
            return pd.DataFrame(columns=headers)
            
        return pd.concat(result_data, ignore_index=True)
    
    def process_and_save(self) -> List[str]:
        """
        处理Excel文件中的所有工作表并保存为CSV
        
        Returns:
            保存的CSV文件路径列表
        """
        # 读取Excel文件
        excel_file = pd.ExcelFile(self.file_path)
        
        # 获取所有工作表
        all_sheets = excel_file.sheet_names
        
        # 确保工作表类型列表长度与工作表数量匹配
        if len(self.sheet_types) < len(all_sheets):
            self.sheet_types.extend(['transfer'] * (len(all_sheets) - len(self.sheet_types)))
        elif len(self.sheet_types) > len(all_sheets):
            self.sheet_types = self.sheet_types[:len(all_sheets)]
        
        saved_files = []
        
        # 处理每个工作表
        for i, (sheet_name, sheet_type) in enumerate(zip(all_sheets, self.sheet_types)):
            # 读取工作表数据
            sheet_data = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)
            
            # 根据工作表类型处理数据
            if sheet_type == 'transfer':
                processed_data = self._process_transfer_sheet(sheet_data)
            else:  # transient
                processed_data = self._process_transient_sheet(sheet_data)
            
            # 保存为CSV，使用新的命名格式
            output_file = f"{self.output_prefix}-{i+1}-{sheet_type}.csv"
            processed_data.to_csv(output_file, index=False)
            saved_files.append(output_file)
            
        return saved_files
    
    def get_sheet_info(self) -> Dict[str, str]:
        """
        获取Excel文件中所有工作表的信息
        
        Returns:
            工作表名称和类型的字典
        """
        excel_file = pd.ExcelFile(self.file_path)
        all_sheets = excel_file.sheet_names
        
        # 确保工作表类型列表长度与工作表数量匹配
        if len(self.sheet_types) < len(all_sheets):
            self.sheet_types.extend(['transfer'] * (len(all_sheets) - len(self.sheet_types)))
        elif len(self.sheet_types) > len(all_sheets):
            self.sheet_types = self.sheet_types[:len(all_sheets)]
        
        return {sheet: sheet_type for sheet, sheet_type in zip(all_sheets, self.sheet_types)} 