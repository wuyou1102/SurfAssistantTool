# -*- encoding:UTF-8 -*-
import threading
import logging
import types
from random import choice
import six


class ErrorCodeField(int):
    def __new__(cls, error_code, message=u""):
        obj = int.__new__(cls, error_code)
        obj.MSG = message
        return obj


class ErrorCodeMetaClass(type):
    def __new__(cls, name, bases, namespace):
        code_message_map = {}
        for k, v in namespace.items():
            if getattr(v, '__class__', None) and isinstance(v, ErrorCodeField):
                if code_message_map.get(v):
                    raise ValueError("duplicated codde {0} {1}".format(k, v))
                code_message_map[v] = getattr(v, 'MSG', "")
        namespace["CODE_MESSAGE_MAP"] = code_message_map
        return type.__new__(cls, name, bases, namespace)


class BaseErrorCode(six.with_metaclass(ErrorCodeMetaClass)):
    CODE_MESSAGE_MAP = NotImplemented


class ErrorCode(BaseErrorCode):
    TARGET_ALREADY_EXIST = ErrorCodeField(10001, "Same target is already running.")
    TARGET_NOT_FUNCTION = ErrorCodeField(10002, "The target cannot be called.It's not a function.")


__log = logging.getLogger(__name__)

__thread_pool = dict()


def query_thread():
    __log.debug(msg="%-10s|%50s" % ("STATE", "NAME"))
    for k, v in __thread_pool.items():
        __log.debug(msg="%-10s|%50s" % ("RUNNING" if v.isAlive() else "DONE", k))


def append_work(target, allow_dupl=False, **kwargs):
    query_thread()
    if not isinstance(target, types.FunctionType) and not isinstance(target, types.MethodType):
        __log.error(ErrorCode.TARGET_NOT_FUNCTION.MSG)
        return False
    if allow_dupl:
        return __append_thread_duplicate(target=target, **kwargs)
    else:
        return __append_thread(target=target, **kwargs)


def is_alive(name):
    _thread = __thread_pool.get(name)
    if _thread and _thread.isAlive():
        return True
    return False


def __append_thread_duplicate(target, **kwargs):
    def add_suffix(name):
        name += ':'
        for x in range(20):
            name += choice('0123456789ABCDEF')
        return name

    name = kwargs.get('thread_name', target.__name__)
    name = add_suffix(name)
    kwargs['thread_name'] = name
    return __start_thread(target=target, **kwargs)


def __append_thread(target, **kwargs):
    thread_name = kwargs.get('thread_name', target.__name__)
    kwargs['thread_name'] = thread_name
    _thread = __thread_pool.get(thread_name)
    if _thread and _thread.isAlive():
        __log.warn(ErrorCode.TARGET_ALREADY_EXIST)
        return False
    return __start_thread(target=target, **kwargs)


def __start_thread(target, thread_name, **kwargs):
    t = threading.Thread(target=target, kwargs=kwargs)
    t.setDaemon(True)
    __thread_pool[thread_name] = t
    t.start()
    __log.debug(msg="%-10s|%50s" % ("STARTED", thread_name))
    return True


if __name__ == '__main__':
    pass
