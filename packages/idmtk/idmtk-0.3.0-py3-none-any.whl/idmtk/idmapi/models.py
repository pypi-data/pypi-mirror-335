from pydantic import BaseModel


class AuthLogin(BaseModel):
    """
    :username: 用户名
    :password: 密码
    """

    username: str
    password: str


class ReturnAuthLogin(BaseModel):
    """
    :is_login_success: 登录是否成功
    :token: token
    """

    is_login_success: bool
    token: str = ""


class AddOrUpdateCategory(BaseModel):
    """
    :id: 分类ID
    :category_name: 分类名称
    :token: 登录token
    """

    id: str
    category_name: str
    token: str


class ReturnAddOrUpdateCategory(BaseModel):
    """
    :is_update_success: 是否保存成功
    :return_message: 请求返回信息
    """

    is_update_success: bool
    return_message: str


class DeleteCategory(BaseModel):
    """
    :id: 分类ID
    :token: 登录token
    """

    id: str
    token: str


class ReturnDeleteCategory(BaseModel):
    """
    :is_delete_success: 是否删除成功
    :return_message: 请求返回信息
    """

    is_delete_success: bool
    return_message: str


class GetUserCategoryList(BaseModel):
    """
    :token: 鉴权
    """

    token: str


class ReturnCategoryList(BaseModel):
    """
    :is_get_success: 是否获取成功
    :category_list_data: 用户分类管理列表
    """

    is_get_success: bool
    category_list_data: list[str] = []


class GetUserAllCategories(BaseModel):
    """
    :token: 鉴权
    """

    token: str


class ReturnUserAllCategories(BaseModel):
    """
    :is_get_success: 是否获取成功
    :categories: 用户分类列表
    """

    is_get_success: bool
    categories: list[str] = []


class GetUserCollectPageList(BaseModel):
    """
    :project_id: 项目ID
    :category_id：分类ID
    :is_share：0: 查询我的 1: 分享数据集
    :share_type：ALL：公开 USERS：私有定向分享
    :page：页码
    :size：页大小
    :token: 鉴权
    """

    project_id: str
    category_id: str
    is_share: int
    share_type: str
    page: int
    size: int
    token: str


class ReturnUserCollectPageList(BaseModel):
    """
    :is_get_success: 是否获取成功
    :user_collect_page_list: 用户分类列表
    """

    is_get_success: bool
    user_collect_page_list: dict[str, str] = {}


class UpdateCollectInfo(BaseModel):
    """
    :collect_data_id：集合ID
    :collect_name：集合名称
    :category_id：分类ID
    :category_name：分类名称
    :project_ids：关联的项⽬ID集合
    :project_names：关联的项⽬名称集合
    :share_type：ALL：公开 USERS：私有定向分享
    :share_users：分享的用户集合【登录名】
    :share_user_ids：分享的用户ID集合
    :token: 鉴权
    """

    collect_data_id: str
    collect_name: str
    category_id: str
    category_name: str
    project_ids: list[str]
    project_names: list[str]
    share_type: str
    share_users: list[str]
    share_user_ids: list[str]
    token: str


class ReturnUpdateCollectInfo(BaseModel):
    """
    :is_update_success: 是否更新成功
    :return_message: 请求返回信息
    """

    is_update_success: bool
    return_message: str


class ShowSoftwareList(BaseModel):
    """
    :software_type：软件类型：0:全部1:纳观2:微观3:介观4:宏观
    :token: 鉴权
    """

    software_type: int
    token: str


class ReturnShowSoftwareList(BaseModel):
    """
    :is_get_success: 是否获取成功
    :software_list: 仓库软件列表
    """

    is_get_success: bool
    software_list: list[str] = []


class SubmitNfsJob(BaseModel):
    """
    :software_id：使⽤的软件ID
    :project_id：项⽬ID
    :project_name：项⽬名称
    :job_name：作业名称
    :app_name：软件名称
    :env_params：环境变量
    :execute_instruct：运⾏指令
    :use_node：使⽤节点
    :use_cpu_raw：使⽤核数
    :job_desc: 作业描述
    :files: 作业⽂件
    :token: 鉴权
    """

    software_id: int
    project_id: int
    project_name: str
    job_name: str
    app_name: str
    env_params: str
    execute_instruct: str
    use_node: int
    use_cpu_raw: int
    job_desc: str
    files: list[str]
    token: str


class ReturnSubmitNfsJob(BaseModel):
    """
    :is_submit_success: 是否提交成功
    :return_message: 请求返回信息
    """

    is_submit_success: bool
    return_message: str



