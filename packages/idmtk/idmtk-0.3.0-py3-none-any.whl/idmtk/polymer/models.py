# Athor: 刘禺 IDM-D
# Created: 2024-06-28
# utils模块的类型系统


from pydantic import BaseModel

class FuncRawFileToList(BaseModel):
    """
    :file_name: 读取的文件名
    """

    file_name: str


class ReturnFuncRawFileToList(BaseModel):
    """
    :file_lines_to_list: 文件逐行转为列表
    """

    file_lines_to_list: list[str]


class FuncGetLinesWithNumber(BaseModel):
    """
    :data_list: 原始文件转化的数据列表
    :number: 开头行的数字
    """

    data_list: list[str]
    number: int

class ReturnFuncGetLinesWithNumber(BaseModel):
    """
    :lines_with_number: 以特定数字开头向下21行的数据
    """

    lines_with_number: list[str]


class FuncCalAverage(BaseModel):
    """
    :data_list: 21个元素的列表
    """

    data_list: list[str]


class ReturnFuncCalAverage(BaseModel):
    """
    :t_average: 温度的平均
    :d_average: 密度的平均
    """

    t_average: float
    d_average: float


class FuncCalALotOfCoordinates(BaseModel):
    """
    :file_name: 文件名
    :number_list: 数据起始点的列表
    """

    file_name: str
    number_list: list[int]


class ReturnFuncCalALotOfCoordinates(BaseModel):
    """
    :t_average_list: 温度平均值列表
    :d_average_list: 密度平均值列表
    """

    t_average_list: list[float]
    d_average_list: list[float]


class FuncGenerateNumberList(BaseModel):
    """
    :start_number: 起始数字
    :step: 数据步长
    :list_length: 列表的元素个数
    """

    start_number: int
    step: int
    list_length: int


class ReturnFuncGenerateNumberList(BaseModel):
    """
    :number_list: 生成的开头数字列表
    """

    number_list: list[int]


class FuncCalCoordinatesWithNumberList(BaseModel):
    """
    :file_name: 文件名
    :start_number: 起始数字
    :step: 数据步长
    :list_length: 列表的元素个数
    """

    file_name: str
    start_number: int = 590000
    step: int = 200000
    list_length: int = 26


class ReturnFuncCalCoordinatesWithNumberList(BaseModel):
    """
    :coord_t_list: 温度值列表
    :coord_d_list: 密度值列表
    """

    coord_t_list: list[float]
    coord_d_list: list[float]


class FuncCalMse(BaseModel):
    """
    :coord_t_list: 温度值列表
    :coord_d_list: 密度值列表
    """

    coord_t_list: list[float]
    coord_d_list: list[float]


class ReturnFuncCalMse(BaseModel):
    """
    :mse_x_list: 每个计算的mse对应的横坐标
    :mse_list: mse的列表
    """

    mse_x_list: list[float]
    mse_list: list[float]


class FuncReadLargestMseTemperature(BaseModel):
    """
    :mse_x_list: 每个计算的mse对应的横坐标
    :mse_list: mse的列表
    """

    mse_x_list: list[float]
    mse_list: list[float]


class ReturnFuncReadLargestMseTemperature(BaseModel):
    """
    :largest_mse_temperature: 最大mse出对应的温度
    """

    largest_mse_temperature: float


class FuncReadLargestMseIndex(BaseModel):
    """
    :mse_list: mse的列表
    """

    mse_list: list[float]


class ReturnFuncReadLargestMseIndex(BaseModel):
    """
    :largest_mse_index: 最大mse出对应的索引
    """

    largest_mse_index: int


class FuncCalTg(BaseModel):
    """
    :coord_t_list: 温度值列表
    :coord_d_list: 密度值列表
    :largest_mse_index: 最大mse出对应的索引
    """

    coord_t_list: list[float]
    coord_d_list: list[float]
    largest_mse_index: int


class ReturnFuncCalTg(BaseModel):
    """
    :tg: 玻璃化转变温度
    """

    tg: float
