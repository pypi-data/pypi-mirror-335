from .config import BASE_URL
from requests import Response # type: ignore
from .api import send_get_request, send_post_request
from .exception import GetRequestError, PostRequestError
from .models import (
    AddOrUpdateCategory,
    DeleteCategory,
    GetUserAllCategories,
    GetUserCategoryList,
    GetUserCollectPageList,
    ReturnAddOrUpdateCategory,
    ReturnCategoryList,
    ReturnDeleteCategory,
    ReturnUpdateCollectInfo,
    ReturnUserAllCategories,
    ReturnUserCollectPageList,
    UpdateCollectInfo,
    ReturnShowSoftwareList,
    ShowSoftwareList,
    SubmitNfsJob,
    ReturnSubmitNfsJob,
)


def add_or_update_category(
    id: str, category_name: str, token: str
) -> ReturnAddOrUpdateCategory:
    """
    添加或修改数据集分类API
    :id: 分类ID
    :id type: str
    :category_name: 分类名称
    :category_name type: str
    :token: 登录token
    :token type: str
    :return: 包含两个属性：
            is_update_success: 是否保存成功, bool
            return_message: 请求返回信息, str
    :rtype: class
    """

    params = AddOrUpdateCategory(id=id, category_name=category_name, token=token)
    return _add_or_update_category(params=params)


def _add_or_update_category(params: AddOrUpdateCategory) -> ReturnAddOrUpdateCategory:
    """
    添加或修改数据集分类API
    """

    url: str = f"{BASE_URL}/simulation/personal/data/addOrUpdateCategory"
    json_data: dict[str, str | int | list[str]] = {"id ": params.id, "categoryName": params.category_name}
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {params.token}",
    }
    try:
        response: Response = send_post_request(
            url=url, json_data=json_data, headers=headers
        )
        if response.json()["code"] == 200:
            return ReturnAddOrUpdateCategory(
                is_update_success=True, return_message=response.json()["message"]
            )
        else:
            return ReturnAddOrUpdateCategory(
                is_update_success=False, return_message=response.json()["message"]
            )
    except PostRequestError as e:
        print(f"Caught exception: {e}, Status Code: {e.status_code}")
        return ReturnAddOrUpdateCategory(is_update_success=False, return_message=str(e))


def delete_category(id: str, token: str) -> ReturnDeleteCategory:
    """
    添加或修改数据集分类API
    :id: 分类ID
    :id type: str
    :token: 登录token
    :token type: str
    :return: 包含两个属性：
            is_delete_success: 是否删除成功, bool
            return_message: 请求返回信息, str
    :rtype: class
    """

    params = DeleteCategory(id=id, token=token)
    return _delete_category(params=params)


def _delete_category(params: DeleteCategory) -> ReturnDeleteCategory:
    """
    添加或修改数据集分类API
    """

    url: str = f"{BASE_URL}/simulation/personal/data/deleteCategory/{params.id}"
    json_data: dict[str, str | int | list[str]] = {"id ": params.id}
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {params.token}",
    }
    try:
        response: Response = send_post_request(
            url=url, json_data=json_data, headers=headers
        )
        if response.json()["code"] == 200:
            return ReturnDeleteCategory(
                is_delete_success=True, return_message=response.json()["message"]
            )
        else:
            return ReturnDeleteCategory(
                is_delete_success=False, return_message=response.json()["message"]
            )
    except PostRequestError as e:
        print(f"Caught exception: {e}, Status Code: {e.status_code}")
        return ReturnDeleteCategory(is_delete_success=False, return_message=str(e))


def get_user_category_list(token: str) -> ReturnCategoryList:
    """
    获取用户分类管理列表API
    :token: 登录token
    :token type: str
    :return: 包含两个属性：
            is_get_success: 是否获取成功, bool
            category_list_data: 用户分类管理列表, list
    :rtype: class
    """

    params = GetUserCategoryList(token=token)
    return _get_user_category_list(params)


def _get_user_category_list(params: GetUserCategoryList) -> ReturnCategoryList:
    """
    获取用户分类管理列表API
    """

    url: str = f"{BASE_URL}/simulation/personal/data/getUserCategoryList"
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {params.token}",
    }
    try:
        response: Response = send_get_request(url=url, headers=headers)
        if response.json()["code"] == 200:
            return ReturnCategoryList(
                is_get_success=True, category_list_data=response.json()["data"]
            )
        else:
            return response.json()["message"]
    except GetRequestError as e:
        print(f"Caught exception: {e}, Status Code: {e.status_code}")
        return ReturnCategoryList(is_get_success=False)


def get_user_all_categories(token: str) -> ReturnUserAllCategories:
    """
    获取用户的分类列表API
    :token: 登录token
    :token type: str
    :return: 包含两个属性：
            is_get_success: 是否获取成功, bool
            categories: 用户分类列表, list
    :rtype: class
    """

    params = GetUserAllCategories(token=token)
    return _get_user_all_categories(params)


def _get_user_all_categories(params: GetUserAllCategories) -> ReturnUserAllCategories:
    """
    获取用户的分类列表API
    """

    url: str = f"{BASE_URL}/simulation/personal/data/getUserAllCategories"
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {params.token}",
    }
    try:
        response: Response = send_get_request(url=url, headers=headers)
        if response.json()["code"] == 200:
            return ReturnUserAllCategories(
                is_get_success=True, categories=response.json()["data"]
            )
        else:
            return response.json()["message"]
    except GetRequestError as e:
        print(f"Caught exception: {e}, Status Code: {e.status_code}")
        return ReturnUserAllCategories(is_get_success=False)


def get_user_collect_page_list(
    *,
    project_id: str = "",
    category_id: str = "",
    is_share: int,
    share_type: str = "",
    page: int,
    size: int,
    token: str,
) -> ReturnUserCollectPageList:
    """
    获取数据集列表API
    :project_id: 项目ID
    :project_id type: str
    :category_id：分类ID
    :category_id type: str
    :is_share：0: 查询我的 1: 分享数据集
    :is_share type: int
    :share_type：ALL：公开 USERS：私有定向分享
    :share_type type: str
    :page：页码
    :page type: int
    :size：页大小
    :size type: int
    :token: 登录token
    :token type: str
    :return: 包含两个属性：
            is_get_success: 是否获取成功, bool
            user_collect_page_list: 用户分类列表, dict
    :rtype: class
    """

    params = GetUserCollectPageList(
        project_id=project_id,
        category_id=category_id,
        is_share=is_share,
        share_type=share_type,
        page=page,
        size=size,
        token=token,
    )
    return _get_user_collect_page_list(params)


def _get_user_collect_page_list(
    params: GetUserCollectPageList,
) -> ReturnUserCollectPageList:
    """
    获取数据集列表API
    """

    url: str = f"{BASE_URL}/simulation/personal/data/getUserCollectPageList"
    request_params: dict[str, str | int] = {
        "projectId": params.project_id,
        "categoryId": params.category_id,
        "isShare": params.is_share,
        "shareType": params.share_type,
        "page": params.page,
        "size": params.size,
    }
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {params.token}",
    }
    try:
        response: Response = send_get_request(
            url=url, params=request_params, headers=headers
        )
        if response.json()["code"] == 200:
            return ReturnUserCollectPageList(
                is_get_success=True, user_collect_page_list=response.json()["data"]
            )
        else:
            return response.json()["message"]
    except GetRequestError as e:
        print(f"Caught exception: {e}, Status Code: {e.status_code}")
        return ReturnUserCollectPageList(is_get_success=False)


def update_collect_info(
    *,
    collect_data_id: str,
    collect_name: str = "",
    category_id: str = "",
    category_name: str = "",
    project_ids: list[str] | None = None,
    project_names: list[str] | None = None,
    share_type: str = "",
    share_users: list[str] | None = None,
    share_user_ids: list[str] | None = None,
    token: str,
) -> ReturnUpdateCollectInfo:
    """
    更新数据集信息API
    :collect_data_id：集合ID
    :collect_data_id type: str
    :collect_name：集合名称
    :collect_name type: str
    :category_id：分类ID
    :category_id type: str
    :category_name：分类名称
    :category_name type: str
    :project_ids：关联的项⽬ID集合
    :project_ids type: list
    :project_names：关联的项⽬名称集合
    :project_names type: list
    :share_type：ALL：公开 USERS：私有定向分享
    :share_type type: str
    :share_users：分享的用户集合【登录名】
    :share_users type: list
    :share_user_ids：分享的用户ID集合
    :share_user_ids type: list
    :token: 登录token
    :token type: str
    :return: 包含两个属性：
            is_update_success: 是否更新成功, bool
            return_message: 请求返回信息, str
    :rtype: class
    """

    if share_user_ids is None:
        share_user_ids = []
    if share_users is None:
        share_users = []
    if project_names is None:
        project_names = []
    if project_ids is None:
        project_ids = []
    params = UpdateCollectInfo(
        collect_data_id=collect_data_id,
        collect_name=collect_name,
        category_id=category_id,
        category_name=category_name,
        project_ids=project_ids,
        project_names=project_names,
        share_type=share_type,
        share_users=share_users,
        share_user_ids=share_user_ids,
        token=token,
    )
    return _update_collect_info(params=params)


def _update_collect_info(params: UpdateCollectInfo) -> ReturnUpdateCollectInfo:
    """
    更新数据集信息API
    """

    url: str = f"{BASE_URL}/simulation/personal/data/updateCollectInfo"
    json_data: dict[str, str | int | list[str]] = {
        "collectDataId": params.collect_data_id,
        "collectName": params.collect_name,
        "categoryId": params.category_id,
        "categoryName": params.category_name,
        "projectIds": params.project_ids,
        "projectNames": params.project_names,
        "shareType": params.share_type,
        "shareUsers": params.share_users,
        "shareUserIds": params.share_user_ids,
    }
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {params.token}",
    }
    try:
        response: Response = send_post_request(
            url=url, json_data=json_data, headers=headers
        )
        if response.json()["code"] == 200:
            return ReturnUpdateCollectInfo(
                is_update_success=True, return_message=response.json()["message"]
            )
        else:
            return ReturnUpdateCollectInfo(
                is_update_success=False, return_message=response.json()["message"]
            )
    except PostRequestError as e:
        print(f"Caught exception: {e}, Status Code: {e.status_code}")
        return ReturnUpdateCollectInfo(is_update_success=False, return_message=str(e))


def show_software_list(*, software_type: int = 0, token: str) -> ReturnShowSoftwareList:
    """
    获取仓库列表API
    :software_type：页大小
    :software_type type: int
    :token: 登录token
    :token type: str
    :return: 包含两个属性：
            :is_get_success: 是否获取成功
            :software_list: 仓库软件列表
    :rtype: class
    """

    params = ShowSoftwareList(software_type=software_type, token=token)
    return _show_software_list(params)


def _show_software_list(params: ShowSoftwareList) -> ReturnShowSoftwareList:
    """
    获取仓库列表API
    """

    url: str = f"{BASE_URL}/simulation/software/showList"
    request_params: dict[str, str | int] = {"type": params.software_type}
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {params.token}",
    }
    try:
        response: Response = send_get_request(
            url=url, params=request_params, headers=headers
        )
        if response.json()["code"] == 200:
            return ReturnShowSoftwareList(
                is_get_success=True, software_list=response.json()["data"]
            )
        else:
            return response.json()["message"]
    except GetRequestError as e:
        print(f"Caught exception: {e}, Status Code: {e.status_code}")
        return ReturnShowSoftwareList(is_get_success=False)


def submit_nfs_job(
    *,
    software_id: int,
    project_id: int,
    project_name: str,
    job_name: str,
    app_name: str,
    env_params: str,
    execute_instruct: str,
    use_node: int,
    use_cpu_raw: int,
    job_desc: str = "",
    files: list[str],
    token: str,
) -> ReturnSubmitNfsJob:
    """
    在线提交作业API
    :software_id：使⽤的软件ID
    :software_id type: int
    :project_id：项⽬ID
    :project_id type: int
    :project_name：项⽬名称
    :project_name type: str
    :job_name：作业名称
    :job_name type: str
    :app_name：软件名称
    :app_name type: str
    :env_params：环境变量
    :env_params type: str
    :execute_instruct：运⾏指令
    :execute_instruct type: str
    :use_node：使⽤节点
    :use_node type: int
    :use_cpu_raw：使⽤核数
    :use_cpu_raw type: int
    :job_desc: 作业描述
    :job_desc type: str
    :files: 作业⽂件
    :files type: list
    :token: 登录token
    :token type: str
    :return: 包含两个属性：
            is_submit_success: 是否提交成功, bool
            return_message: 请求返回信息, str
    :rtype: class
    """

    params = SubmitNfsJob(
        software_id=software_id,
        project_id=project_id,
        project_name=project_name,
        job_name=job_name,
        app_name=app_name,
        env_params=env_params,
        execute_instruct=execute_instruct,
        use_node=use_node,
        use_cpu_raw=use_cpu_raw,
        job_desc=job_desc,
        files=files,
        token=token,
    )
    return _submit_nfs_job(params=params)


def _submit_nfs_job(params: SubmitNfsJob) -> ReturnSubmitNfsJob:
    """
    在线提交作业API
    """

    url: str = f"{BASE_URL}/simulation/sim/job/submitNfsJob"
    json_data: dict[str, str | int | list[str]] = {
        "softwareId": params.software_id,
        "projectId": params.project_id,
        "projectName": params.project_name,
        "jobName": params.job_name,
        "appName": params.app_name,
        "envParams": params.env_params,
        "executeInstruct": params.execute_instruct,
        "useNode": params.use_node,
        "useCpuRaw": params.use_cpu_raw,
        "jobDesc": params.job_desc,
        "files": params.files,
    }
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {params.token}",
    }
    try:
        response: Response = send_post_request(
            url=url, json_data=json_data, headers=headers
        )
        if response.json()["code"] == 200:
            return ReturnSubmitNfsJob(
                is_submit_success=True, return_message=response.json()["message"]
            )
        else:
            return ReturnSubmitNfsJob(
                is_submit_success=False, return_message=response.json()["message"]
            )
    except PostRequestError as e:
        print(f"Caught exception: {e}, Status Code: {e.status_code}")
        return ReturnSubmitNfsJob(is_submit_success=False, return_message=str(e))
