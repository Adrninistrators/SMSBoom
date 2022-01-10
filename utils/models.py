# -*- coding: utf-8 -*-
# @Time : 2022/1/11 1:44
# @Author : WhaleFall
# @Site : 
# @File : models.py
# @Description : 存放数据模型的地方
from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import constr
import datetime


class Apis(SQLModel, table=True):
    """Api Model"""
    id: Optional[int] = Field(default=None, primary_key=True)  # 数据库自己生成的id
    method: str = "GET" or "POST"
    ua: Optional[
        str] = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 " \
               "Safari/534.50"
    url: str
    data: str


class Logs(SQLModel, table=True):
    """logs model"""
    id: Optional[int] = Field(default=None, primary_key=True)  # 数据库自己生成的id
    timestamp: int = datetime.datetime.now().timestamp()  # 时间戳
    phone: Optional[constr(max_length=25)]  # 电话号码
