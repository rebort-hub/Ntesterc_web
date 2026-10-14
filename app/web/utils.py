VALUE_ERROR_ZH = {
    "username exists": "用户名已存在",
    "email exists": "邮箱已存在",
    "user not found": "用户不存在",
    "role name exists": "角色名称已存在",
    "role code exists": "角色编码已存在",
    "role not found": "角色不存在",
    "permission name exists": "权限名称已存在",
    "permission code exists": "权限编码已存在",
    "permission not found": "权限不存在",
    "parent permission not found": "父级权限不存在",
    "cannot set self as parent": "不能将自身设为父级",
    "permission has children": "请先删除子权限",
}


def humanize_error(exc: Exception) -> str:
    if isinstance(exc, ValueError):
        msg = str(exc)
        if msg in VALUE_ERROR_ZH:
            return VALUE_ERROR_ZH[msg]
        if msg.startswith("invalid permission type:"):
            return "权限类型无效，可选：menu、button、api"
        return msg
    return "操作失败，请稍后重试"
