from .models import AuthLogin, ReturnAuthLogin
from .config import BASE_URL
from requests import Response #type: ignore
from .api import send_post_request
from .exception import PostRequestError


def login(username: str, password: str) -> ReturnAuthLogin | None:
    """
    登录函数底层
    :username: 用户名
    :username type: str
    :password: 密码
    :password type: str
    :return: 包含两个属性：
            is_login_success: 登录是否成功, bool
            token: token, str
    :rtype: class
    TODO:
        需要改写
    """
    params = AuthLogin(username=username, password=password)
    # return _login(params=params)
    auth_login_return, err = _login(params=params)

    # Exception捕获后如何处理
    # 现阶段先把exception当作一个值传出，仿照go的逻辑
    # 登录失败场景可考虑raise Exception，引发panic
    # 其他场景也需要对应处理方式
    # 现在的逻辑是把Exception留到之后处理，估计会在token鉴权的时候panic或失败
    # 错误向上传递的话后续写log容易
    if err is not None:
        return None
    else:
        return auth_login_return


def _login(params: AuthLogin) -> tuple[ReturnAuthLogin, Exception | None]:
    """
    登录函数底层
    """

    url: str = f"{BASE_URL}/admin/login"
    json_data: dict[str, str | int | list[str]] = {
        "loginName": params.username,
        "password": params.password,
    }
    headers: dict[str, str] = {"Content-Type": "application/json"}
    try:
        response: Response = send_post_request(
            url=url, json_data=json_data, headers=headers
        )
        if response.status_code == 200:
            token = response.json()["token"]
            return ReturnAuthLogin(is_login_success=True, token=token), None
        else:
            return ReturnAuthLogin(is_login_success=False), None
    except PostRequestError as e:
        print(f"Caught exception: {e}, Status Code: {e.status_code}")
        return ReturnAuthLogin(is_login_success=False), e
