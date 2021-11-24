import argparse

from bot import Bot

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, help="""
    The token used for the bot to work.
    If not indicated, get an environnment variable with the name 'TOKEN'.
    """)

    parser.add_argument("--prefix", type=str, help="""
    The prefix used for the bot.
    If not indicated, get an environnment variable with the name 'PREFIX'.""")

    parser.add_argument("--debug", "-D", default=False, action='store_true', help="""
    Check if the bot should run in debug mode.
    If not indicated, the bot will run in production mode.
    """)

    args = vars(parser.parse_args())
    bot = Bot(args)
    bot.run_bot()
