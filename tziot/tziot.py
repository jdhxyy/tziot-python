"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
天泽物联网sdk
Authors: jdh99 <jdh821@163.com>
"""

import tziot.config as config
import tziot.apply as apply
import tziot.fpipe as fpipe
import tziot.conn as conn
import tziot.parsecmp as parsecmp

import dcompy as dcom
import utzpy as utz


def call(pipe: int, dst_ia: int, rid: int, timeout: int, req: bytearray) -> (bytearray, int):
    """
    RPC同步调用
    :param pipe: 通信管道
    :param dst_ia: 目标ia地址
    :param rid: 服务号
    :param timeout: 超时时间,单位:ms.为0表示不需要应答
    :param req: 请求数据.无数据可填bytearray()或者None
    :return: 返回值是应答字节流和错误码.错误码非0表示调用失败
    """
    if apply.parent.ia == utz.IA_INVALID or not apply.parent.is_conn:
        return None, dcom.SYSTEM_ERROR_RX_TIMEOUT

    if pipe >= fpipe.PIPE_NET:
        pipe = apply.parent.pipe
    return dcom.call(config.PROTOCOL_NUM, pipe, dst_ia, rid, timeout, req)


def register(rid: int, callback):
    """
    注册DCOM服务回调函数
    :param rid: 服务号
    :param callback: 回调函数.格式: func(req bytearray) (bytearray, int)
    :return: 返回值是应答和错误码.错误码为0表示回调成功,否则是错误码
    """
    dcom.register(config.PROTOCOL_NUM, rid, callback)


def init_system():
    config.init()
    apply.init()
    conn.init()
    parsecmp.init()
