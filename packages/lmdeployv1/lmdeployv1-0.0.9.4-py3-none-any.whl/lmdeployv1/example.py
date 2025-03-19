#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Copyright (c) 2024 Baidu, Inc. 
# All rights reserved.
#
# File    : example
# Author  : zhoubohan
# Date    : 2024/12/6
# Time    : 11:37
# Description :
"""
from lmdeployv1.api import BatchChatCompletionRequest, LimiterConfig
from lmdeployv1.client import (
    LMDeployClient,
    build_batch_chat_messages,
    build_chat_messages,
)

endpoint_uri = "http://10.211.18.203:8312/ep-gxhukbdy"
limit_config = LimiterConfig(limit=1, interval=1, delay=True, max_delay=60)
client = LMDeployClient(
    endpoint=endpoint_uri,
    context={
        "OrgID": "ab87a18d6bdf4fc39f35ddc880ac1989",
        "UserID": "ab87a18d6bdf4fc39f35ddc880ac1989",
    },
    limiter_config=limit_config,
)

image_url = (
    "http://tools.bj.bcebos.com/images/an.jpeg?authorization=bce-auth-v1%2FALTAKTZhksfCVgZJ96g46t21lA%2F2024"
    "-12-06T03%3A41%3A30Z%2F-1%2Fhost%2F524f024252d15ac895f6f41ecf53ff57a53a03cb70d1656a46ace7e39d572041"
)

message = {image_url: "Is there any cat in the image? only answer yes or no."}


def test_chat_completion():
    """
    test_chat_completion
    :return:
    """
    req = build_chat_messages(message)
    resp = client.chat_completion(messages=req)
    choice = [c.message for c in resp.choices]
    assert len(choice[0].content) > 1

    print(f"chat response: {choice[0].content}")


image_urls = [
    "http://10.92.54.93:8412/resource/windmill/store/01de5ebf9cbb4eaa92c4919624d996dd/workspaces/wsgsdwed/projects/"
    "spiproject/annotationsets/as-7hhRdQqg/mYgrP67d/data/images/dog.4.jpg",
    "http://10.92.54.93:8412/resource/windmill/store/01de5ebf9cbb4eaa92c4919624d996dd/workspaces/wsgsdwed/projects/"
    "spiproject/annotationsets/as-7hhRdQqg/mYgrP67d/data/images/dog.3.jpg",
    "http://10.92.54.93:8412/resource/windmill/store/01de5ebf9cbb4eaa92c4919624d996dd/workspaces/wsgsdwed/projects/"
    "spiproject/annotationsets/as-7hhRdQqg/mYgrP67d/data/images/cat.9.jpg",
    "http://10.92.54.93:8412/resource/windmill/store/01de5ebf9cbb4eaa92c4919624d996dd/workspaces/wsgsdwed/projects/"
    "spiproject/annotationsets/as-7hhRdQqg/mYgrP67d/data/images/cat.8.jpg",
    "http://10.92.54.93:8412/resource/windmill/store/01de5ebf9cbb4eaa92c4919624d996dd/workspaces/wsgsdwed/projects/"
    "spiproject/annotationsets/as-7hhRdQqg/mYgrP67d/data/images/cat.7.jpg",
]


def test_batch_chat_completion():
    """
    test_batch_chat_completion
    :return:
    """
    messages = []
    for i in image_urls:
        messages.append({i: "图中的动物是什么"})
    msg = build_batch_chat_messages(messages)
    resp = client.batch_chat_completion(
        BatchChatCompletionRequest(
            messages=msg,
            temperature=0,
            top_p=1,
            repetition_penalty=1,
        )
    )
    choice = [c.message for c in resp.choices]
    assert len(choice[0].content) > 1

    print(f"batch chat response: {choice[0].content}")


if __name__ == "__main__":
    test_chat_completion()
    test_batch_chat_completion()
