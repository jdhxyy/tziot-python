"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
连接父路由
Authors: jdh99 <jdh821@163.com>
"""

import tziot.apply as apply
import tziot.config as config
import tziot.fpipe as fpipe
import tziot.standardlayer as standardlayer

import knocky as knock
import utzpy as utz
import lagan
import threading
import time


def init():
    knock.register(utz.HEADER_CMP, utz.CMP_MSG_TYPE_ACK_CONNECT_PARENT_ROUTER, deal_ack_connect_parent_router)
    threading.Thread(target=_conn_thread).start()
    threading.Thread(target=_conn_timeout).start()


def deal_ack_connect_parent_router(req: bytearray, *args) -> (bytearray, bool):
    """dealAckConnectParentRouter 处理应答连接帧.返回值是应答数据和应答标志.应答标志为false表示不需要应答"""
    if len(req) == 0:
        lagan.warn(config.TAG, "deal conn failed.payload len is wrong:%d", len(req))
        return None, False

    j = 0
    if req[j] != 0:
        lagan.warn(config.TAG, "deal conn failed.error code:%d", req[j])
        return None, False
    j += 1

    if len(req) != 2:
        lagan.warn(config.TAG, "deal conn failed.payload len is wrong:%d", len(req))
        return None, False

    apply.parent.is_conn = True
    apply.parent.cost = req[j]
    apply.parent.timestamp = int(time.time())
    lagan.info(config.TAG, "conn success.parent ia:0x%x cost:%d", apply.parent.ia, apply.parent.cost)
    return None, False


def _conn_thread():
    while True:
        # 如果网络通道不开启则无需连接
        if not fpipe.pipe_is_allow_send(fpipe.PIPE_NET):
            time.sleep(1)
            continue

        if apply.parent.ia != utz.IA_INVALID:
            lagan.info(config.TAG, "send conn frame")
            _send_conn_frame()

        if apply.parent.ia == utz.IA_INVALID:
            time.sleep(1)
        else:
            time.sleep(config.CONN_INTERVAL)


def _send_conn_frame():
    security_header = utz.SimpleSecurityHeader()
    security_header.next_head = utz.HEADER_CMP
    security_header.pwd = config.local_pwd
    payload = utz.simple_security_header_to_bytes(security_header)

    body = bytearray()
    body.append(utz.CMP_MSG_TYPE_CONNECT_PARENT_ROUTER)
    # 前缀长度
    body.append(64)
    # 子膜从机固定单播地址
    body += bytearray(utz.IA_LEN)
    # 开销值
    body.append(0)
    body = utz.bytes_to_flp_frame(body, True, 0)

    payload += body

    header = utz.StandardHeader()
    header.version = utz.PROTOCOL_VERSION
    header.frame_index = utz.generate_frame_index()
    header.payload_len = len(payload)
    header.next_head = utz.HEADER_SIMPLE_SECURITY
    header.hops_limit = 0xff
    header.src_ia = config.local_ia
    header.dst_ia = config.core_ia

    standardlayer.send(payload, header, apply.parent.pipe)


def _conn_timeout():
    while True:
        if apply.parent.ia == utz.IA_INVALID or not apply.parent.is_conn:
            time.sleep(1)
            continue

        if int(time.time()) - apply.parent.timestamp > config.CONN_TIMEOUT_MAX:
            apply.parent.ia = utz.IA_INVALID
            apply.parent.is_conn = False

        time.sleep(1)


def is_conn() -> bool:
    """是否连接核心网"""
    return apply.parent.ia != utz.IA_INVALID and apply.parent.is_conn
