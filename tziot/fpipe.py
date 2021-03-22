"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
管道操作
Authors: jdh99 <jdh821@163.com>
"""

import tziot.config as config
import tziot.standardlayer as standardlayer
import tziot.fdcom as fdcom
import tziot.apply as apply
import tziot.tziot as ftziot

import socket
import threading
import lagan
import dcompy as dcom
import utzpy as utz

from typing import Callable

PIPE_NET = 0xffff


class _Api:
    # 是否允许发送.函数原型:func() bool
    is_allow_send = None  # type: Callable[[], bool]
    # 发送.函数原型:func(pipe: int, data: bytearray)
    send = None  # type: Callable[[int, bytearray], None]


_pipes = dict()
_pipe_num = 0
_socket = None
_is_first_run = True


def bind_pipe_net(ia: int, pwd: str, ip: str, port: int) -> int:
    """ 绑定网络管道.绑定成功后返回管道号"""
    global _socket, _is_first_run

    if _is_first_run:
        _is_first_run = False
        ftziot.init_system()

    if _socket is not None:
        lagan.warn(config.TAG, "already bind pipe net")
        return PIPE_NET

    config.local_pwd = pwd
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.bind((ip, port))
    _bind(PIPE_NET, ia, _socket_tx, _socket_is_allow_send)
    threading.Thread(target=_socket_rx).start()

    return PIPE_NET


def _socket_rx():
    global _socket
    while True:
        data, address = _socket.recvfrom(config.FRAME_MAX_LEN)
        if len(data) == 0:
            continue
        lagan.info(config.TAG, 'udp rx:%r len:%d', address, len(data))
        lagan.print_hex(config.TAG, lagan.LEVEL_DEBUG, bytearray(data))
        pipe_receive(dcom.addr_to_pipe(address[0], address[1]), data)


def _socket_tx(pipe: int, data: bytearray):
    ip, port = dcom.pipe_to_addr(pipe)
    _socket.sendto(data, (ip, port))
    lagan.info(config.TAG, "udp send:ip:%s port:%d len:%d", ip, port, len(data))
    lagan.print_hex(config.TAG, lagan.LEVEL_DEBUG, data)


def _socket_is_allow_send() -> bool:
    return True


def pipe_receive(pipe: int, data: bytearray):
    """管道接收.pipe是发送方的管道号.如果是用户自己绑定管道,则在管道中接收到数据需回调本函数"""
    standardlayer.rx(pipe, data)


def bind_pipe(ia: int, send, is_allow_send) -> int:
    """
    绑定管道.绑定成功后返回管道号
    :param ia: 设备单播地址
    :param send: 发送函数.格式:func(dst_pipe: int, data: bytearray)
    :param is_allow_send: 是否允许发送函数.格式:func() -> bool
    :return: 管道号
    """
    global _is_first_run

    if _is_first_run:
        _is_first_run = False
        ftziot.init_system()

    pipe = _get_pipe_num()
    _bind(pipe, ia, send, is_allow_send)
    return pipe


def _get_pipe_num() -> int:
    global _pipe_num

    _pipe_num += 1
    return _pipe_num


def _bind(pipe: int, ia: int, send, is_allow_send):
    config.local_ia = ia

    api = _Api()
    api.send = send
    api.is_allow_send = is_allow_send

    _pipes[pipe] = api
    fdcom.init_dcom()


def pipe_is_allow_send(pipe: int) -> bool:
    if pipe >= PIPE_NET:
        pipe = PIPE_NET

    if pipe not in _pipes:
        return False
    return _pipes[pipe].is_allow_send()


def pipe_send(pipe: int, data: bytearray):
    if pipe == 0:
        return

    if pipe >= PIPE_NET:
        if PIPE_NET not in _pipes:
            return
        v = _pipes[PIPE_NET]
    else:
        if pipe not in _pipes:
            return
        v = _pipes[PIPE_NET]

    if pipe == PIPE_NET:
        if apply.parent.ia == utz.IA_INVALID or not apply.parent.is_conn:
            return
        v.send(apply.parent.pipe, data)
    else:
        v.send(pipe, data)
