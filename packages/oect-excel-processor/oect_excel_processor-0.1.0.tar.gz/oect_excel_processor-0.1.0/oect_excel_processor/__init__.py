"""
OECT Excel Processor - 用于处理OECT性能测试后的Excel数据并转换为CSV格式

这个包提供了用于处理特定格式Excel文件并转换为CSV格式的工具，
专门针对OECT（有机电化学晶体管）性能测试数据。
"""

from .excel_processor import ExcelProcessor
from .batch_processor import BatchExcelProcessor

__version__ = '0.1.0'
__author__ = 'OECT Research Team'
__all__ = ['ExcelProcessor', 'BatchExcelProcessor'] 