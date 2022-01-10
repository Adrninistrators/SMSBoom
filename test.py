import click


# 命令行组的用法

@click.group()
def cli():
    pass


@click.command(help="打招呼")
def test():
    click.echo("你好!")


cli.add_command(test)

if __name__ == "__main__":
    cli()
