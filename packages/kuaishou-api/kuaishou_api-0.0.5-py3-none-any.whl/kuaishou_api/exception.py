# __all__ = [
#     # warnings
#     # exceptions
#     'kuaishouException',
#     'NeedLoginException',
# ]


class kuaishouException(Exception):
    pass


class NeedLoginException(kuaishouException):
    def __init__(self, what):
        """
        使用某方法需要登录而当前客户端未登录

        :param str|unicode what: 当前试图调用的方法名
        """
        self.what = what

    def __repr__(self):
        return '需要登录才能使用 [{self.what}] 方法。'.format(self=self)

    __str__ = __repr__


class NeedAccessTokenException(kuaishouException):

    def __repr__(self):
        return '需要用户 access-token 才能使用这个接口！'.format(self=self)

    __str__ = __repr__


class LoginError(kuaishouException):
    """
    所有登录中发生的错误
    """
