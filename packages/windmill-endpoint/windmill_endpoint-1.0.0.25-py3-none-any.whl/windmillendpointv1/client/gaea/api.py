# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2024/8/13 14:13
# @Author : zhangzhijun06
# @Email: zhangzhijun06@baidu.com
# @File : __init__.py.py
# @Software: PyCharm
"""
from typing import Union, Any, List

from pydantic import BaseModel, Field


class ModelMetaData(BaseModel):
    """
    ModelMetaData
    """

    image_id: str = Field(default="image_id", description="图像 ID")
    camera_id: str = Field(default="camera_id", description="摄像头 ID")
    camera_fps: int = Field(default=25, ge=1, description="摄像头帧率")
    frame_pos: int = Field(default=0, ge=0, description="帧位置")
    timestamp: str = Field(default="", description="时间戳")

    block_scale_width: float = Field(default=1.0, ge=0.0, description="块宽缩放比例")
    block_scale_height: float = Field(default=1.0, ge=0.0, description="块高缩放比例")
    block_offset_width: float = Field(default=0.0, ge=0.0, description="块宽偏移")
    block_offset_height: float = Field(default=0.0, ge=0.0, description="块高偏移")
    whole_scale_width: float = Field(default=1.0, ge=0.0, description="整体宽缩放比例")
    whole_scale_height: float = Field(default=1.0, ge=0.1, description="整体高缩放比例")


class InferConfig(BaseModel):
    """
    InferConfig
    """
    top_p: float = Field(default=0.6, ge=0.0, le=1.0, description="核采样")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="采样温度")
    repetition_penalty: float = Field(default=1.2, ge=1.0, le=1.5, description="重复惩罚")
    sequence_id: int = Field(default=1, ge=0, description="序列ID，用于标识生成序列")
    sequence_start: bool = Field(default=True, description="序列起始标志")
    prompt: str = Field(default="", max_length=1000, description="提示词")


class ModelInferRequest(BaseModel):
    """model inference request"""

    meta: ModelMetaData = None
    image_buffer: bytes = b""
    model_name: str = ""
    infer_config: InferConfig = None
    is_track: bool = False
    is_group_content: bool = False


class OCR(BaseModel):
    """OCR"""

    word: str = ""
    direction: Union[str, int] = ""
    confidence: float = 0.0


class Category(BaseModel):
    """Category"""

    id: str = ""
    name: str = ""
    confidence: float = 0.0
    value: Any = None
    super_category: str = ""


class Prediction(BaseModel):
    """Prediction"""

    bbox: List[float] = None
    confidence: float = 0.0
    segmentation: List[float] = None
    area: float = 0.0
    ocr: OCR = None
    features: List[float] = None
    bbox_id: int = 0
    track_id: int = 0
    categories: List[Category] = None
    question: str = ""
    question_id: str = ""
    answer: str = ""


class Parameter(BaseModel):
    """Parameter"""

    name: str = ""
    namespace: str = ""
    type: str = ""
    current: str = ""
    default: str = ""
    description: str = ""
    step: str = ""
    range: str = ""
    enum: str = ""
    exclude: str = ""


class ModelParameter(BaseModel):
    """ModelParameter"""

    model_name: str = ""
    model_type: str = ""
    parameters: List[Parameter] = None


class ModelInferOutput(BaseModel):
    """ModelInferOutput"""

    image_id: str = ""
    predictions: List[Prediction] = None
    model_parameters: List[ModelParameter] = None
