#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Copyright (c) 2024 Baidu, Inc.
# All rights reserved.
#
# File    : example
# Author  : zhoubohan
# Date    : 2024/12/30
# Time    : 11:37
# Description :
"""
import httpx
from lmdeployv1.api import LimiterConfig
from lmdeployv1.client import LMDeployClient
from windmillendpointv1.client.gaea.api import ModelInferRequest, InferConfig
from windmillendpointv1.client.gaea.infer import infer

endpoint_uri = "http://10.211.18.203:8312/ep-gxhukbdy"
limit_config = LimiterConfig(limit=1, interval=1, delay=True, max_delay=60)
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


def get_image_bytes(url: str) -> bytes:
    """
    get_image_bytes
    """
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


req = ModelInferRequest(
    infer_config=InferConfig(
        top_p=1,
        temperature=0,
        repetition_penalty=1,
        prompt="图中的动物是什么",
    )
)

lmdeploy_client = LMDeployClient(
    endpoint=endpoint_uri,
    context={
        "OrgID": "ab87a18d6bdf4fc39f35ddc880ac1989",
        "UserID": "ab87a18d6bdf4fc39f35ddc880ac1989",
    },
    limiter_config=limit_config,
)


def gaea_lmdeploy():
    """
    gaea_lmdeploy
    """
    for i in image_urls:
        req.image_buffer = get_image_bytes(i)
        resp = infer(lmdeploy_client, req)
        print(resp)


if __name__ == "__main__":
    gaea_lmdeploy()
