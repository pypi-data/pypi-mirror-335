# Athor: 刘禺 IDM-D
# Created: 2024-12-09
# 小角散射edf图片转为png、jpeg等格式图片

import gc
import os
import fabio  # type: ignore
import matplotlib.pyplot as plt
import numpy as np
from .models import EdfFileInit, EdfSavefig

from typing import Any
from numpy.typing import NDArray


class EdfFile:
    def __init__(
        self,
        *,
        file_path: str,
    ) -> None:
        """类初始化，读入文件路径，对edf格式图片进行预处理

        Args:
            file_path (str): edf文件的路径

        Raises:
            e: 使用fabio库时的读取错误
        """
        self.params = EdfFileInit(
            file_path=file_path,
        )

        try:
            edf_data: Any = fabio.open(self.params.file_path).data
            self.edf_data = edf_data
        except Exception as e:
            print("读取数据失败！")
            raise e

    def setup_fig(self) -> None:
        """画图前的图像处理，初始化各种plt参数

        Returns:
            Figure: plt画图的基础设置
        """
        plt.rcParams["axes.facecolor"] = "black"
        plt.figure(figsize=(9, 12))
        plt.subplots_adjust(
            left=0.1, bottom=0.02, right=1, top=0.98, wspace=0.1, hspace=0.1
        )

    def image_show(self) -> None:
        """显示二维图，首先调用初始化程序，画图，展示图像"""
        self.setup_fig()
        plt.imshow(X=self.edf_data, norm="log", cmap="jet")
        plt.colorbar()
        plt.show()

    def image_save(self, *, save_dir: str = "", save_name: str, dpi: int = 600) -> None:
        """保存二维图

        Args:
            save_dir (str): 保存路径，不包含文件名
            save_name (str): 文件名，不包含扩展名，默认为png格式
            dpi (int, optional): 图像清晰度. Defaults to 600.
        """
        params = EdfSavefig(save_dir=save_dir, save_name=save_name, dpi=dpi)
        self.setup_fig()
        plt.imshow(X=self.edf_data, norm="log", cmap="jet")
        plt.colorbar()
        plt.savefig(os.path.join(params.save_dir, params.save_name))
        plt.cla()
        plt.clf()
        gc.collect()

    def to_array(self) -> NDArray[np.float64]:
        """将edf图转为array，供用户设置参数画图用。

        Returns:
            NDArray[np.float64]: 返回numpy的array数据
        """
        edf_array = np.array(self.edf_data)
        return edf_array
