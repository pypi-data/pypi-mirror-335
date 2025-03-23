# -*- coding: utf-8 -*-
# @Time    : 2024/8/8 14:52
# @Author  : Chris
# @Email   : 10512@qq.com
# @File    : notify.py
# @Software: PyCharm

import time

import requests
from loguru import logger

from abu import retry_with_method


def escape_markdown(text):
    # 需要转义的特殊字符
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


@retry_with_method(3)
def send_msg_to_telegram(bot_token, chat_id, content, proxy: str = ''):
    """
    通过telegram机器人发消息给指定用户或群组
    :param bot_token:   机器人token
    :param chat_id:     用户或群组id
    :param content:     发送的内容
    :param proxy:       telegram在国内需要使用国外代理
    :return:            发送成功返回True
    """

    content_list = []
    if len(content) > 4000:
        for i in range(0, len(content), 4000):
            single = content[i:i + 4000]
            if single.startswith("```") or single.endswith("```"):
                single = f'```\n{single.replace("```", "")}\n```'
            else:
                single = escape_markdown(single)
            content_list.append(single)
    else:
        content = escape_markdown(content) if not content.startswith("```") else content
        content_list.append(content)

    for content in content_list:
        for _ in range(3):
            try:
                data = {
                    "chat_id": chat_id,
                    "text": content,
                    "parse_mode": "MarkdownV2"
                }
                if proxy:
                    ret = requests.post(f"https://api.telegram.org/{bot_token}/sendMessage", data=data, verify=False,
                                        proxies={
                                            "https": proxy if proxy.startswith("http") else "http://" + proxy}).json()
                else:
                    ret = requests.post(f"https://api.telegram.org/{bot_token}/sendMessage", data=data).json()

                if ret.get("ok"):
                    logger.success("发送Telegram消息成功！")
                    break
                else:
                    logger.error(f"推送消息失败..\n内容:{content}\n结果:{ret}")
            except BaseException as e:
                logger.error(e.__repr__())
                logger.critical(f"推送消息失败..\n内容:{content}")


@retry_with_method(3)
def send_msg_to_bark(api, title: str = "Message", body: str = ""):
    """
    通过bark推送消息
    :param api:     bark的api
    :param title:   标题
    :param body:    内容
    """
    data = {"body": body, "title": title}
    for _ in range(3):
        try:
            ret = requests.post(
                f"{api}/?icon=https://i.bmp.ovh/imgs/2021/11/7995dd6ff8ae2e74.png",
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                },
                json=data,
            ).json()

            if ret.get("code") == 200:
                logger.success(f"推送消息成功")
                break
            else:
                logger.error(f"推送消息失败..将在10秒后重新尝试...")
                time.sleep(9)
                continue
        except BaseException:
            time.sleep(9)


class QQ:
    def __init__(self, api):
        self.api = api
        self.session = requests.session()
        self.session.headers = {
            "Authorization": "Bearer Chris"
        }

    def send_msg_group(self, group_id, message):
        data = {
            "group_id": group_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": message
                    }
                }
            ]
        }
        return self.session.post(self.api + 'send_group_msg', json=data).json()

    def send_msg_private(self, user_id, message):
        data = {
            "user_id": user_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": message
                    }
                }
            ]
        }
        return self.session.post(self.api + 'send_private_msg', json=data).json()
