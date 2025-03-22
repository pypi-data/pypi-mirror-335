import os
from pydantic import BaseModel, field_validator


class EdfFileInit(BaseModel):
    """
    :file_path: edf文件路径，包含文件名
    """
    file_path: str

    @field_validator("file_path")
    @classmethod
    def check_file_path_end_with_edf(cls, value: str) -> str:
        """检查文件读取路径是否以'.edf'结尾

        Args:
            value (str): file_path

        Raises:
            ValueError: file_path应当以'.edf'结尾。

        Returns:
            str: file_path
        """
        if value.endswith(".edf"):
            return value
        else:
            raise ValueError("file_path应当以'.edf'结尾。")


class EdfSavefig(BaseModel):
    """
    :save_dir: 保存路径
    :save_name: 保存的文件名
    :dpi: 图片清晰度
    """
    save_dir: str
    save_name: str
    dpi: int

    @field_validator("save_name")
    @classmethod
    def check_save_name(cls, value: str) -> str:
        """检查保存文件名的扩展名
            不应有扩展名
        
        Args:
            value(str): save_name
            
        Raise:
            ValueError: 文件名不应包含扩展名
        
        Return:
            str: save_name
        """

        # 截取保存文件名的扩展名
        if "." in value:
            raise ValueError(
                """
                文件名不应包含扩展名
                """
            )
        else:
            return value
        
class HermanInput(BaseModel):
    """
    :filename: dat文件路径,包含文件名
    :degree: 主要信号分布于纤维径向或薄膜面内方向请输入90;
             主要信号分布于纤维轴向或薄膜面外方向请输入0;
             输入其他内容将无法计算，提示错误。
    """
    filename: str
    degree: int

    @field_validator("filename")
    @classmethod
    def check_filename_end_with_dat(cls, value: str) -> str:
        """检查文件读取路径是否以'.dat'结尾"""
        if value.endswith(".dat"):
            return value
        else:
            raise ValueError("filename应当以'.dat'结尾。")

    @field_validator("degree")
    @classmethod
    def check_degree(cls, value: int):
        if value in (0, 90):
            return value
        else:
            raise ValueError("degree输入只能是0或90度")
