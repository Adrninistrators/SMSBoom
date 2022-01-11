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
from pathlib import Path

config = Config()  # 实例化配置


@click.group()
def cli():
    """命令行组"""
    pass


@click.command(help="初始化应用")
@click.option('--reset', flag_value=True)
def build(reset: bool):
    if reset:
        click.echo(f"删除数据库:{reset}")
        Path(config.SQLITE_PATH).unlink()
    engine = create_engine(config.DATABASE_URI, echo=True)
    SQLModel.metadata.create_all(engine)
    click.echo("初始化数据库成功!")


cli.add_command(build)

if __name__ == "__main__":
    cli()
