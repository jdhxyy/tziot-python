# 海萤物联网教程：Python SDK
本文博客链接:[http://blog.csdn.net/jdh99](http://blog.csdn.net/jdh99),作者:jdh,转载请注明.

欢迎前往社区交流：[海萤物联网社区](http://www.ztziot.com)

[在线文档地址](https://jdhxyy.github.io/tziot)

## 简介
此SDK适用于Python3.5及以上版本。使用此SDK可以让节点连接海萤物联网，与其他节点通信。节点可以是终端设备，也可以是个人电脑上的程序，可以使用此SDK与其他节点通信，并可以以服务的形式开放自己的能力。

Python SDK是海萤物联网的SDK之一，主要有如下功能：

- 连接海萤物联网
- 与其他节点通信
- 以服务的形式开放节点自身的能力

## 特点
基于此SDK可以极大降低物联网的开发门槛，可以实现：
- 一行代码连接网络
- 一行代码开放服务
- 一行代码通信

## 开源
- [github上的项目地址](https://github.com/jdhxyy/tziot-python)
- [gitee上的项目地址](https://gitee.com/jdhxyy/tziot-python)

## 安装
```text
pip install tziot
```

## 背景知识
- [海萤物联网教程：IA地址格式及地址申请方法](https://blog.csdn.net/jdh99/article/details/115340195)

- [海萤物联网教程：物联网RPC框架Python DCOM](https://blog.csdn.net/jdh99/article/details/115374729)

## API
```python
def bind_pipe_net(ia: int, pwd: str, ip: str, port: int) -> int:
    """ 绑定网络管道.绑定成功后返回管道号"""
    
def bind_pipe(ia: int, send, is_allow_send) -> int:
    """
    绑定管道.绑定成功后返回管道号
    :param ia: 设备单播地址
    :param send: 发送函数.格式:func(dst_pipe: int, data: bytearray)
    :param is_allow_send: 是否允许发送函数.格式:func() -> bool
    :return: 管道号
    """

def pipe_receive(pipe: int, data: bytearray):
    """管道接收.pipe是发送方的管道号.如果是用户自己绑定管道,则在管道中接收到数据需回调本函数"""

def is_conn() -> bool:
    """是否连接核心网"""

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

def register(rid: int, callback):
    """
    注册DCOM服务回调函数
    :param rid: 服务号
    :param callback: 回调函数.格式: func(pipe: int, src_ia: int, req: bytearray) (bytearray, int)
    :return: 返回值是应答和错误码.错误码为0表示回调成功,否则是错误码
    """

def config_core_param(ia: int, ip: str, port: int):
    """配置核心网参数"""

def config_dcom_param(retry_num: int, retry_interval: int):
    """
    配置dcom参数
    :param retry_num: 重发次数
    :param retry_interval: 重发间隔.单位:ms
    """
```

### 默认参数
当前默认的参数：

参数|值
---|---
DCOM重发次数|5
DCOM重发间隔|500ms

调用config_core_param函数可以修改DCOM参数。

config_core_param函数可以修改海萤物联网平台默认地址，使用默认值即可，不需要调用函数修改。

### 绑定管道
tziot包中封装了dcom包，在绑定管道时会初始化DCOM。

tziot中调用bind_pipe函数可以绑定自定义管道，如果使用自定义管道，则需应用中调用pipe_receive函数将接收到的数据发送给tziot包。

绑定网络管道是绑定管道的一个特例，如果节点可以直接连接互联网（比如使用以太网或者wifi），则调用bind_pipe_net函数即可，不需要使用bind_pipe函数和pipe_receive函数。

- 示例：绑定网络管道，节点地址是0x2140000000000101，本地端口号是12021
```python
pipe = bind_pipe_net(0x2140000000000101, pwd, "0.0.0.0", 12021)
```
返回的是管道号pipe。后续使用call函数与其他节点通信，需要使用此管道号。

绑定管道后sdk会自动连接海萤物联网，可以调用is_conn函数查看连接是否成功。

### 注册服务
节点可以通过注册服务开放自身的能力。

```python
def register(rid: int, callback):
    """
    注册DCOM服务回调函数
    :param rid: 服务号
    :param callback: 回调函数.格式: func(pipe: int, src_ia: int, req: bytearray) (bytearray, int)
    :return: 返回值是应答和错误码.错误码为0表示回调成功,否则是错误码
    """
```

注册函数中，每个服务号（rid），都可以绑定一个服务。

- 示例：假设节点2140::101是智能插座，提供控制和读取开关状态两个服务：

```python
tziot.register(1, control_service)
tziot.register(2, get_state_service)


def control_service(pipe: int, src_ia: int, req: bytearray) -> (bytearray, int):
	"""控制开关服务.返回值是应答和错误码.错误码为0表示回调成功,否则是错误码"""
	if req[0] == 0:
		off()
	else:
		on()
	return None, dcom.SystemOK


def get_state_service(pipe: int, src_ia: int, req: bytearray) -> (bytearray, int):
	"""读取开关状态服务.返回值是应答和错误码.错误码为0表示回调成功,否则是错误码"""
	return bytearray([state()]), dcom.SystemOK
```

### 调用目的节点服务
```python
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
```

同步调用会在获取到结果之前阻塞。节点可以通过同步调用，调用目标节点的函数或者服务。timeout字段是超时时间，单位是毫秒。如果目标节点超时未回复，则会调用失败。如果超时时间填0，则表示不需要目标节点回复。

- 示例：2141::102节点控制智能插座2141::101开关状态为开

```python
resp, errCode = tziot.call(1, 0x2140000000000101, 3000, bytearray([1]))
```

- 示例：2141::102节点读取智能插座2141::101开关状态

```python
resp, errCode = tziot.call(2, 0x2140000000000101, 3000, None)
if errCode == dcom.SystemOK:
	print("开关状态:", resp[0])
```

## 请求和应答数据格式
建议使用结构体来通信。详情可参考： [海萤物联网教程：物联网RPC框架Python DCOM](https://blog.csdn.net/jdh99/article/details/115374729) 中的数据格式章节。

## 完整示例
示例以与海萤物联网中的python版本的ntp服务通信为例。

### python版本的ntp服务器开源地址
- [github上的项目地址](https://github.com/jdhxyy/ntp-python)
- [gitee上的项目地址](https://gitee.com/jdhxyy/ntp-python)

### ntp服务介绍
[python版本的海萤物联网ntp服务上线](https://blog.csdn.net/jdh99/article/details/115395187)

ntp服务器地址：
```text
0x2141000000000405
```

当前提供两个服务：

服务号|服务
---|---
1|读取时间1
2|读取时间2.返回的是结构体

#### 读取时间服务1
- CON请求：空或者带符号的1个字节。

当CON请求为空时，则默认为读取的是北京时间（时区8）。

也可以带1个字节表示时区号。这个字节是有符号的int8。

小技巧，可以使用0x100减去正值即负值。比如8对应的无符号数是0x100-8=248。

- ACK应答：当前时间的字符串

当前时间字符串的格式：2006-01-02 15:04:05 -0700 MST

#### 读取时间服务2.返回的是结构体
- CON请求：格式与读取时间服务1一致

- ACK应答：
```c
struct {
    // 时区
    uint8 TimeZone
    uint16 Year
    uint8 Month
    uint8 Day
    uint8 Hour
    uint8 Minute
    uint8 Second
    // 星期
    uint8 Weekday
}
```

### 开放服务示例
```python
"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
网络校时服务
Authors: jdh99 <jdh821@163.com>
"""

import config

import tziot
import dcompy as dcom
import lagan
import sbc

from datetime import datetime, timedelta

TAG = 'ntp'

# 应用错误码
# 内部错误
ERROR_CODE_INTERNAL_ERROR = 0x40
# 接收格式错误
ERROR_CODE_RX_FORMAT = 0x41

# rid号
# 读取时间.返回的是字符串
RID_GET_TIME1 = 1
# 读取时间.返回的是结构体
RID_GET_TIME2 = 2


class AckRidGetTime2(sbc.LEFormat):
    _fields_ = [
        # (字段名, c类型)
        # 时区
        ('time_zone', sbc.c_uint8),
        ('year', sbc.c_int16),
        ('month', sbc.c_uint8),
        ('day', sbc.c_uint8),
        ('hour', sbc.c_uint8),
        ('minute', sbc.c_uint8),
        ('second', sbc.c_uint8),
        # 星期
        ('weekday', sbc.c_uint8),
    ]


def main():
    config.init()

    lagan.load(0)
    lagan.set_filter_level(lagan.LEVEL_INFO)
    lagan.enable_color(True)
    dcom.set_filter_level(lagan.LEVEL_WARN)

    tziot.bind_pipe_net(config.LOCAL_IA, config.local_pwd, config.LOCAL_IP, config.LOCAL_PORT)
    tziot.register(RID_GET_TIME1, ntp_service1)
    tziot.register(RID_GET_TIME2, ntp_service2)


def ntp_service1(pipe: int, src_ia: int, req: bytearray) -> (bytearray, int):
    """校时服务.返回值是应答和错误码.错误码为0表示回调成功,否则是错误码"""
    ip, port = dcom.pipe_to_addr(pipe)

    if len(req) == 0:
        time_zone = 8
    elif len(req) == 1:
        time_zone = req[0]
        if time_zone >= 0x80:
            time_zone = -(0x100 - time_zone)
    else:
        lagan.warn(TAG, "ip:%s port:%d ia:0x%x ntp failed.len is wrong:%d", ip, port, src_ia, len(req))
        return None, ERROR_CODE_RX_FORMAT

    now = datetime.utcnow() + timedelta(hours=time_zone)
    if time_zone >= 0:
        s = '%04d-%02d-%02d %02d:%02d:%02d +%02d00 MST' % (now.year, now.month, now.day, now.hour, now.minute,
                                                            now.second, time_zone)
    else:
        s = '%04d-%02d-%02d %02d:%02d:%02d -%02d00 MST' % (now.year, now.month, now.day, now.hour, now.minute,
                                                            now.second, -time_zone)
    lagan.info(TAG, 'ip:%s port:%d ntp time:%s', ip, port, s)
    return tziot.str_to_bytearray(s), 0


def ntp_service2(pipe: int, src_ia: int, req: bytearray) -> (bytearray, int):
    """校时服务.返回值是应答和错误码.错误码为0表示回调成功,否则是错误码"""
    ip, port = dcom.pipe_to_addr(pipe)

    if len(req) == 0:
        time_zone = 8
    elif len(req) == 1:
        time_zone = req[0]
        if time_zone >= 0x80:
            time_zone = -(0x100 - time_zone)
    else:
        lagan.warn(TAG, "ip:%s port:%d ia:0x%x ntp failed.len is wrong:%d", ip, port, src_ia, len(req))
        return None, ERROR_CODE_RX_FORMAT

    now = datetime.utcnow() + timedelta(hours=time_zone)
    t = AckRidGetTime2()
    t.time_zone = time_zone
    t.year = now.year
    t.month = now.month
    t.day = now.day
    t.hour = now.hour
    t.minute = now.minute
    t.second = now.second
    t.weekday = now.isoweekday()
    lagan.info(TAG, 'ip:%s port:%d ntp time:%04d-%02d-%02d %02d:%02d:%02d +%02d00 MST', ip, port, t.year, t.month,
               t.day, t.hour, t.minute, t.second, t.time_zone)
    return t.struct_to_bytearray(), 0


if __name__ == '__main__':
    main()
```

### 读取时间服务1
节点2141::401读取ntp服务器的服务1，并打印时间字符串。

```python
def main():
    pipe = tziot.bind_pipe_net(0x2141000000000401, pwd, '0.0.0.0', 12021)
    while not tziot.is_conn():
        pass
    resp, err = tziot.call(pipe, 0x2141000000000005, 1, 3000, bytearray())
    print(err, resp)
}
```

输出结果：
```text
0 b'2021-04-03 16:48:50 +0800 MST'
```

### 读取时间服务2
ntp服务器的2号是结构体形式的时间。

```python
import tziot
import sbc


class AckRidGetTime(sbc.LEFormat):
    _fields_ = [
        # (字段名, c类型)
        # 时区
        ('time_zone', sbc.c_uint8),
        ('year', sbc.c_int16),
        ('month', sbc.c_uint8),
        ('day', sbc.c_uint8),
        ('hour', sbc.c_uint8),
        ('minute', sbc.c_uint8),
        ('second', sbc.c_uint8),
        # 星期
        ('weekday', sbc.c_uint8),
    ]


def main():
    pipe = tziot.bind_pipe_net(0x2141000000000401, pwd, '0.0.0.0', 12021)
    while not tziot.is_conn():
        pass
    resp, err = tziot.call(pipe, 0x2141000000000005, 2, 3000, bytearray())
    if err != 0:
        return

    ack = AckRidGetTime()
    if not ack.bytearray_to_struct(resp):
        return
    print(ack.time_zone, ack.year, ack.month, ack.day, ack.hour, ack.minute, ack.second, ack.weekday)


if __name__ == '__main__':
    main()
```

输出结果：
```text
8 2021 4 3 16 47 21 6
```


