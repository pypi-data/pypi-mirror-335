#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/12
# @Author  : yanxiaodong
# @File    : evaluator.py
"""
import numpy as np
import pyarrow as pa
from typing import Optional, Dict, Callable

import bcelogger
import ray
import pyarrow.json as pajson
import pandas as pd

from lmdeployv1.client import LMDeployClient
from windmillendpointv1.client.gaea.api import ModelInferRequest, InferConfig
from windmillendpointv1.client.gaea.infer import infer
from windmilltrainingv1.client.training_api_dataset import ANNOTATION_FORMAT_MS_SWIFT
from vistudio_image_analysis.operator.swift_formatter import SWIFTFormatter
from vistudio_image_analysis.config.old_config import Config
from vistudio_image_analysis.operator.infer import Infer


def evaluator(
        endpoint: str,
        dataset_uri: str,
        metric: Callable,
        category: str,
        output_uri: Optional[str] = "./",
        annotation_format: Optional[str] = "COCO",
        prefer_model_server_kind: Optional[str] = "LMDeploy",
        model_name: Optional[str] = "",
        infer_config: Optional[Dict] = {}):
    """
    evaluate model on dataset and metric, save result to output_uri.
    """
    # 1. 根据 annotation format 解析 dataset_uri，转换为 vistudio 格式
    if annotation_format == ANNOTATION_FORMAT_MS_SWIFT:
        block_size = 100 << 20
        ds = ray.data.read_json(paths=dataset_uri,
                                read_options=pajson.ReadOptions(block_size=block_size),
                                parse_options=pajson.ParseOptions(newlines_in_values=True))

        swift_formatter = SWIFTFormatter()
        ds_dict = swift_formatter.to_vistudio_v1(ds=ds)
        image_ds = ds_dict["image_ds"]
        annotation_ds = ds_dict["annotation_ds"]

        image_df = image_ds.to_pandas()
        annotation_df = annotation_ds.to_pandas()
        merged_df = pd.merge(annotation_df, image_df, left_on='image_id', right_on='image_id')
        merged_df['annotations'] = \
            merged_df['annotations'].apply(lambda x: x if isinstance(x, (np.ndarray, list)) else [x])
        annotation_ds = ray.data.from_arrow(pa.Table.from_pandas(merged_df))

        labels = []
    else:
        raise ValueError(f"{annotation_format} is not supported")

    # 2. infer 获取推理结果
    def _infer(batch):
        file_uris = batch['file_uri'].tolist()

        answer = []
        for idx, file_uri in enumerate(file_uris):
            image_buffer = open(file_uri, 'rb').read()

            req = ModelInferRequest(image_buffer=image_buffer,
                                    model_name=model_name,
                                    infer_config=InferConfig(**infer_config))
            if prefer_model_server_kind == "LMDeploy":
                client = LMDeployClient(endpoint=endpoint)
                req.infer_config.prompt = batch["annotations"][idx][0]["question"]
                req.is_group_content = True
            else:
                raise ValueError(f"{prefer_model_server_kind} is not supported")

            try:
                resp = infer(infer_client=client, req=req)
                if resp is not None and len(resp) > 0:
                    answer.append(resp[0].predictions[0].answer)
                bcelogger.info("Successfully inferred {}".format(file_uri))
            except Exception as err:
                bcelogger.error("failed to infer {}, error {}".format(file_uri, err), exc_info=True)

        batch["answer"] = answer

        return batch

    infer_annotation_ds = \
        annotation_ds.map_batches(lambda batch: _infer(batch), batch_size=1, batch_format="pandas", concurrency=1)

    # 3. infer outputs 转换为 vistudio 格式
    infer_operator = Infer(config=Config({}), operator_params={})
    infer_annotation_ds = \
        infer_operator.to_vistudio_v1(ds=infer_annotation_ds, annotation_set_id="", annotation_set_category=category)

    # 4. 计算 metric
    images = image_ds.to_pandas().to_dict(orient="records")
    references = annotation_ds.to_pandas().to_dict(orient="records")
    predictions = infer_annotation_ds.to_pandas().to_dict(orient="records")
    metric.set_images(images=images)
    metric.set_labels(labels=labels)
    metric(predictions=predictions, references=references, output_uri=output_uri)