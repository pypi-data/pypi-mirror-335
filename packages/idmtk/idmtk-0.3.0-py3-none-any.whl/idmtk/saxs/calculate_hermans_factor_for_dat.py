import argparse
import pandas as pd  # type: ignore
import numpy as np
from numpy.typing import NDArray
from .models import HermanInput


def find_header_row(filename: str) -> int:
    """
    查找包含列名的行号（从0开始计数）。
    假设列名行以'psi(°)', 'Intensity(a.u.)', 'Sigma_I(a.u.)'为列名。
    """
    with open(filename, "r") as file:
        i: int
        line: str
        for i, line in enumerate(file):
            stripped_line: str = line.strip()
            #'psi(°)'是唯一的，并且列名之间由多个空格分隔
            # if 'psi(°)' in stripped_line and 'Intensity(a.u.)' in stripped_line and 'Sigma_I(a.u.)' in stripped_line:
            if "psi(°)" in stripped_line:
                # 直接返回行号，并在后面使用Pandas的read_csv来读取整个DataFrame
                return i
    raise ValueError("没有找到包含列名的行")


def read_dat_data(filename: str) -> NDArray[np.float64]:
    """
    读取dat文件中的数据
    :filename: dat文件的绝对路径
    :return: 数据
    """
    # 找到列名（'psi(°)'）行的行号
    header_row: int = find_header_row(filename)

    # 读取文件，跳过所有在列名行之前的行，并将数据加载到Pandas DataFrame中
    df = pd.read_csv(filename, skiprows=range(header_row), sep=r"\s+")

    # 将DataFrame转换为NumPy数组
    # 注意：DataFrame中需要没有缺失值，否则可能需要先处理缺失值
    data: NDArray[np.float64] = df.to_numpy()
    return data


def get_maxI_data(data: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    获取数组中I的峰值，前后90个数据
    :param data: 数据
    """
    # 找到data[1]的最大值及其索引
    max_index: int = int(np.argmax(data[:, 1]))
    max_value_in_data1: float = data[max_index, 1]
    corresponding_value_in_data0: float = data[max_index, 0]

    #print(f"最大I值: {max_value_in_data1}, psi:{corresponding_value_in_data0}")
    #print(f"最大索引位置: {max_index}")

    # 截取max_I的前后90个数据
    start_index: int
    end_index: int
    new_data: NDArray[np.float64]
    start_index1: int
    start_index2: int
    end_index1: int
    end_index2: int
    extracted_data1: NDArray[np.float64]
    extracted_data2: NDArray[np.float64]
    if max_index - 90 >= 0 and max_index + 90 <= 360:
        # 正常两段数据
        # [x-90,x],[x,x+90]
        start_index = max_index - 90
        end_index = max_index + 90

        new_data = data[start_index:end_index + 1]

    elif max_index - 90 < 0 and max_index + 90 <= 360:
        # 三段数据
        # [360 -(90-x),360],[0,x],[x,x+90]
        start_index1 = 360 - (90 - max_index)
        end_index1 = 360
        extracted_data1 = data[start_index1:end_index1 + 1]

        start_index2 = 0
        end_index2 = max_index + 90
        extracted_data2 = data[start_index2:end_index2 + 1]

        new_data = np.concatenate((extracted_data1, extracted_data2), axis=0)

    elif max_index - 90 >= 0 and max_index + 90 > 360:
        # 三段数据
        # [x-90,x],[x,360],[0,360-x]
        start_index1 = max_index - 90
        end_index1 = 361
        extracted_data1 = data[start_index1:end_index1 + 1]

        start_index2 = 0
        end_index2 = 90 - (360 - max_index)
        extracted_data2 = data[start_index2:end_index2 + 1]

        new_data = np.concatenate((extracted_data1, extracted_data2), axis=0)

    else:
        raise ValueError("数据无效，无法选择峰值，请检查！")

    # 提取数据
    # print(new_data)

    return new_data


def degree_data_range(data: NDArray[np.float64], degree: int) -> NDArray[np.float64]:
    """
    根据参数degree，替换数组中psi的值[0]
    :param data: 数据
    :param degree: 极方向与图0°的夹角，0度或90度
    :return: 提取后的数据数组
    """
    new_data: NDArray[np.float64] = get_maxI_data(data)
    new_data_length: int = new_data.shape[0]
    # print(f"new_data的行数:{new_data_length}")

    incremental_array: NDArray[np.float64]
    if degree == 90:
        # psi[0,180]
        incremental_array = np.arange(0.0, new_data_length, 1.0)
        new_data[:, 0] = incremental_array

        # print(f"更改后的data:{new_data}")

    elif degree == 0:
        # psi[-90,90]
        # incremental_array = np.linspace(-90, 90, new_data_length)
        # incremental_array = np.linspace(-90, 90, 181)
        incremental_array = np.arange(-90.0, 91.0, 1.0)
        # print(f"生成的连续数组:{incremental_array}")

        new_data[:, 0] = incremental_array
        # print(f"更改后的data:{new_data}")

    else:
        raise ValueError("无效的参数")

    # 过滤首列在[0,90]范围内的数据
    filtered_data = new_data[(new_data[:, 0] >= 0) & (new_data[:, 0] <= 90)]
    #print(f"更改后的filter_data:{filtered_data}")

    return filtered_data


def calculate_hermans_factor(data: NDArray[np.float64]) -> tuple[float, float]:
    """
    计算赫尔曼因子。
    :param data: 从Excel中读取的数据
    :return: cos_2_psi, 赫尔曼因子
    """
    tmp_a: int = 0
    tmp_b: int = 0
    row: NDArray[np.float64]
    for row in data:
        # print(f"psi = {row[0]}, I = {row[1]}")
        d_value: float = np.radians(row[0])  # 角度在该行第1列
        e_value: float = row[1]  # 强度数据在该行第2列
        tmp_a += e_value * np.sin(d_value) * np.cos(d_value) * np.cos(d_value)
        tmp_b += e_value * np.sin(d_value)

    if tmp_b == 0:
        raise ValueError("tmp_b cannot be zero")

    cos_2_psi: float = tmp_a / tmp_b  # 公式(1)
    f: float = 0.5 * (3 * cos_2_psi - 1)  # 公式(2)

    return cos_2_psi, f

def hermans_factor_calculate(filename: str, degree: int) -> float:
    """
    计算赫尔曼因子API
    :filename: 文件路径
    :filename type: str
    :degree: 主要信号分布于纤维径向或薄膜面内方向请输入90;
             主要信号分布于纤维轴向或薄膜面外方向请输入0;
             输入其他内容将无法计算，提示错误。
    :degree type: int
    :return: 赫尔曼因子
    :rtype: float
    """
    params = HermanInput(filename=filename, degree=degree)
    
    return _hermans_factor_calculate(params = params) 

def _hermans_factor_calculate(params: HermanInput) -> float:
    try:
        all_dat_data: NDArray[np.float64] = read_dat_data(params.filename)
        data: NDArray[np.float64] = degree_data_range(all_dat_data, params.degree)
        cos_2_psi, hermans_factor = calculate_hermans_factor(data)

    except Exception as e:
        print(f"An error occurred: {e}")

    return hermans_factor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate Hermann Factor from Excel Data."
    )
    parser.add_argument(
        "-f", "--file", type=str, required=True, help="Absolute path to the dat file."
    )
    parser.add_argument(
        "-d",
        "--degree",
        type=int,
        required=True,
        help="The angle between the polar direction and Figure 0°.(0或90)",
    )
    args: argparse.Namespace = parser.parse_args()

    file_path: str = args.file
    degree: int = args.degree

    # print(excel_path, num_columns)

    try:
        all_dat_data: NDArray[np.float64] = read_dat_data(file_path)
        # print(all_dat_data)
        # degree_data_range(all_dat_data, degree)
        data: NDArray[np.float64] = degree_data_range(all_dat_data, degree)
        cos_2_psi, hermans_factor = calculate_hermans_factor(data)
        print("输出：")
        print(f"cos_2_psi: {cos_2_psi}")
        print(f"Hermann Factor: {hermans_factor}")

    except Exception as e:
        print(f"An error occurred: {e}")
