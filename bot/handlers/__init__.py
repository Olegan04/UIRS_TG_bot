from bot.handlers import sheregesh
from bot.handlers import start
from bot.handlers import admin
from bot.handlers import belka

def get_routers():
    return [
        start.router,
        sheregesh.router,
        belka.router,
        admin.router,
    ]