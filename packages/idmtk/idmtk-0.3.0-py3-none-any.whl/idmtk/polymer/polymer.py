# Athor: 刘禺 IDM-D
# Created: 2024-06-28
# 用于聚合物计算tg的代码，未来有聚合物相关的代码也可以一并放在此模块

import re
import numpy as np
from sklearn import linear_model # type: ignore
from sklearn.metrics import mean_squared_error # type: ignore

from .models import (
    FuncCalALotOfCoordinates,
    FuncCalAverage,
    FuncCalCoordinatesWithNumberList,
    FuncCalMse,
    FuncCalTg,
    FuncGenerateNumberList,
    FuncGetLinesWithNumber,
    FuncRawFileToList,
    FuncReadLargestMseIndex,
    # FuncReadLargestMseTemperature, # 未使用
    ReturnFuncCalALotOfCoordinates,
    ReturnFuncCalAverage,
    ReturnFuncCalCoordinatesWithNumberList,
    ReturnFuncCalMse,
    ReturnFuncCalTg,
    ReturnFuncGenerateNumberList,
    ReturnFuncGetLinesWithNumber,
    ReturnFuncRawFileToList,
    ReturnFuncReadLargestMseIndex,
    # ReturnFuncReadLargestMseTemperature, # 未使用
)

# 默认文件读取路径
file_dir = "log"


def set_file_dir(new_file_dir: str) -> None:
    """
    修改默认的读取路径
    :new_file_dir: 修改后的路径名
               如"file", "out"等
               默认路径为"log"
               修改时无需添加开头和结尾的"/"
    :type new_file_dir: str
    """

    global file_dir

    file_dir = new_file_dir


def _raw_file_to_list(params: FuncRawFileToList) -> ReturnFuncRawFileToList:
    """
    原始文件转为数据的列表
    列表里的每个元素对应原始文件的一行
    去掉每个元素最左，右两侧的空格
    去掉换行符
    """

    file_name_to_open: str = "./" + file_dir + "/" + params.file_name

    with open(file=file_name_to_open) as file:
        base_data: list[str] = file.readlines()
        base_data_strip: list[str] = []
        for item in base_data:
            temp_str: str = item.lstrip()
            temp_str = temp_str[:-1]
            temp_str = temp_str.rstrip()
            temp_str = re.sub(r"\s+", ",", temp_str)
            base_data_strip.append(temp_str)

    return ReturnFuncRawFileToList(file_lines_to_list=base_data_strip)


def _get_lines_with_number(
    params: FuncGetLinesWithNumber,
) -> ReturnFuncGetLinesWithNumber:
    """
    从已经去除最前面空格的列表中取出以特定数字开头的一些行
    给定第一行开头的数字
    往后取21行
    """

    number_str: str = str(params.number)

    lines_with_number: list[str] = []

    for i in range(len(params.data_list)):
        if params.data_list[i][0 : len(number_str)] == number_str:
            lines_with_number = params.data_list[i : i + 21]
            break

    return ReturnFuncGetLinesWithNumber(lines_with_number=lines_with_number)


def _cal_average(params: FuncCalAverage) -> ReturnFuncCalAverage:
    """
    输入为21个元素的列表
    列表的每个元素是一列数据，数据类型是str，用逗号分割
    把每个元素的第二个数字和第三个数字取出
    计算第二个数字和第三个数字的平均值
    """

    list_t: list[float] = []
    list_d: list[float] = []

    for item in params.data_list:
        item_list: list[str] = item.split(sep=",")
        list_t.append(float(item_list[1]))
        list_d.append(float(item_list[2]))

    list_t_array = np.array(list_t)
    list_d_array = np.array(list_d)

    t_average = float(np.mean(list_t_array))
    d_average = float(np.mean(list_d_array))

    return ReturnFuncCalAverage(t_average=t_average, d_average=d_average)


def _cal_a_lot_of_coordinates(
    params: FuncCalALotOfCoordinates,
) -> ReturnFuncCalALotOfCoordinates:
    """
    给定一个文件和一个数据起始点的列表，计算多个平均值tuple
    平均值的tuple里有两个数据，可以视为横坐标和纵坐标
    """

    raw_file_to_list_return: ReturnFuncRawFileToList = _raw_file_to_list(
        params=FuncRawFileToList(file_name=params.file_name)
    )

    t_average_list: list[float] = []
    d_average_list: list[float] = []

    for number in params.number_list:
        get_lines_with_number_return: ReturnFuncGetLinesWithNumber = (
            _get_lines_with_number(
                params=FuncGetLinesWithNumber(
                    data_list=raw_file_to_list_return.file_lines_to_list, number=number
                )
            )
        )
        cal_average_return: ReturnFuncCalAverage = _cal_average(
            params=FuncCalAverage(
                data_list=get_lines_with_number_return.lines_with_number
            )
        )
        t_average_list.append(cal_average_return.t_average)
        d_average_list.append(cal_average_return.d_average)

    return ReturnFuncCalALotOfCoordinates(
        t_average_list=t_average_list, d_average_list=d_average_list
    )


def _generate_number_list(
    params: FuncGenerateNumberList,
) -> ReturnFuncGenerateNumberList:
    """
    辅助函数，为了快速生成number_list
    """

    return_list: list[int] = []

    for i in range(params.list_length):
        return_list.append(params.start_number + i * params.step)

    return ReturnFuncGenerateNumberList(number_list=return_list)


def _cal_coordinates_with_number_list(
    params: FuncCalCoordinatesWithNumberList,
) -> ReturnFuncCalCoordinatesWithNumberList:
    """
    高阶函数
    根据输入文件名和number_list，生成两列数据
    """

    generate_number_list_return: ReturnFuncGenerateNumberList = _generate_number_list(
        params=FuncGenerateNumberList(
            start_number=params.start_number,
            step=params.step,
            list_length=params.list_length,
        )
    )

    cal_a_lot_of_coordinates_return: ReturnFuncCalALotOfCoordinates = (
        _cal_a_lot_of_coordinates(
            params=FuncCalALotOfCoordinates(
                file_name=params.file_name,
                number_list=generate_number_list_return.number_list,
            )
        )
    )

    return ReturnFuncCalCoordinatesWithNumberList(
        coord_t_list=cal_a_lot_of_coordinates_return.t_average_list,
        coord_d_list=cal_a_lot_of_coordinates_return.d_average_list,
    )


def _cal_mse(params: FuncCalMse) -> ReturnFuncCalMse:
    """
    根据横纵坐标计算mse
    从右到左计算
    去除几个起始点
    """

    data_counts: int = len(params.coord_t_list)

    x_list: list[float] = []
    mse_list: list[float] = []

    for i in range(data_counts):
        x: list[float] = params.coord_t_list[: i + 1]
        x_array = np.array(x).reshape(-1, 1)
        y: list[float] = params.coord_d_list[: i + 1]
        y_array = np.array(y).reshape(-1, 1)

        linmodel = linear_model.LinearRegression()
        linmodel.fit(x_array, y_array)

        (slope, intercept) = (linmodel.coef_[0], linmodel.intercept_)

        y_pred: list[float] = []
        for item in x:
            y_pred.append(item * slope + intercept)

        mse: float = float(mean_squared_error(y_true=y, y_pred=y_pred))

        x_list.append(x[-1])
        mse_list.append(float(mse))

    return ReturnFuncCalMse(mse_x_list=x_list, mse_list=mse_list)


# 未使用
# def _read_largest_mse_temperature(
#     params: FuncReadLargestMseTemperature,
# ) -> ReturnFuncReadLargestMseTemperature:
#     """
#     通过读取最大的mse，获取对应的温度
#     """

#     mse_array = np.array(params.mse_list)

#     largest_mse_index = np.argmax(mse_array)

#     return ReturnFuncReadLargestMseTemperature(
#         largest_mse_temperature=params.mse_x_list[largest_mse_index]
#     )


def _read_largest_mse_index(
    params: FuncReadLargestMseIndex,
) -> ReturnFuncReadLargestMseIndex:
    """
    通过读取最大的mse，获取对应的温度
    """

    mse_array = np.array(params.mse_list)

    largest_mse_index = np.argmax(mse_array)

    return ReturnFuncReadLargestMseIndex(largest_mse_index=int(largest_mse_index))


def _cal_tg(params: FuncCalTg) -> ReturnFuncCalTg:
    """
    读入坐标元组和切片点的index
    切成两组坐标
    两组分别做线性拟合
    线性拟合结果取交点获得tg
    """

    x_left: list[float] = params.coord_t_list[: params.largest_mse_index]
    x_left_array = np.array(x_left).reshape(-1, 1)
    y_left: list[float] = params.coord_d_list[: params.largest_mse_index]
    y_left_array = np.array(y_left).reshape(-1, 1)

    x_right: list[float] = params.coord_t_list[params.largest_mse_index + 1 :]
    x_right_array = np.array(x_right).reshape(-1, 1)
    y_right: list[float] = params.coord_d_list[params.largest_mse_index + 1 :]
    y_right_array = np.array(y_right).reshape(-1, 1)

    linmodel_left = linear_model.LinearRegression()
    linmodel_left.fit(x_left_array, y_left_array)

    linmodel_right = linear_model.LinearRegression()
    linmodel_right.fit(x_right_array, y_right_array)

    (slope_left, intercept_left) = (linmodel_left.coef_[0], linmodel_left.intercept_)
    (slope_right, intercept_right) = (
        linmodel_right.coef_[0],
        linmodel_right.intercept_,
    )

    tg = (intercept_right - intercept_left) / (slope_left - slope_right)

    # NDarray转为float
    tg = tg[0]

    return ReturnFuncCalTg(tg=tg)


def cal_tg(
    file_name: str,
    start_number: int | None = None,
    step: int | None = None,
    list_length: int | None = None,
) -> float:
    """
    读取一个文件，计算这个文件对应的tg
    :file_name: 文件名
    :type file_name: str
    :start_number: 起始数字
    :type start_number: int | None
    :step: 数据步长
    :type step: int | None
    :list_length: 列表的元素个数
    :type list_length: int | None
    :return: 计算得到的tg
    :rtype: float
    """

    default_params_dict = {
        k: v
        for k, v in zip(
            ("start_number", "step", "list_length"), (start_number, step, list_length)
        )
        if v is not None
    }

    cal_coordinates_with_number_list_return: ReturnFuncCalCoordinatesWithNumberList = (
        _cal_coordinates_with_number_list(
            params=FuncCalCoordinatesWithNumberList(
                file_name=file_name, **default_params_dict
            )
        )
    )

    cal_mse_return: ReturnFuncCalMse = _cal_mse(
        params=FuncCalMse(
            coord_t_list=cal_coordinates_with_number_list_return.coord_t_list,
            coord_d_list=cal_coordinates_with_number_list_return.coord_d_list,
        )
    )

    read_largest_mse_index_return: ReturnFuncReadLargestMseIndex = _read_largest_mse_index(params=FuncReadLargestMseIndex(mse_list=cal_mse_return.mse_list))

    cal_tg_return: ReturnFuncCalTg = _cal_tg(params=FuncCalTg(coord_t_list=cal_coordinates_with_number_list_return.coord_t_list, coord_d_list=cal_coordinates_with_number_list_return.coord_d_list, largest_mse_index=read_largest_mse_index_return.largest_mse_index))

    return cal_tg_return.tg
