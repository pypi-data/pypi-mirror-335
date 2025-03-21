from project.tg_bot.callback.common import BaseCD


class HelloWorldClientCD(BaseCD):
    hello_world: bool = True


class RemoveMessageCD(BaseCD):
    pass
