# -*- coding: utf-8 -*-
# @Time : 2022/1/11 1:31
# @Author : WhaleFall
# @Site : 
# @File : run.py
# @Description : 主运行入口
import click
from config import Config
from utils import *
from sqlmodel import create_engine, SQLModel


@click.group()
def cli():
    """命令行组"""
    pass


@click.command(help="初始化应用")
def build():
    config = Config()
    engine = create_engine(config.DATABASE_URI, echo=True)
    SQLModel.metadata.create_all(engine)
    click.echo("初始化数据库成功!")


cli.add_command(build)

if __name__ == "__main__":
    cli()
