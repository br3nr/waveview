import logging
import os
import functools
from discord.ext.commands import Context


class BrennerLog:
    __instance = None

    @staticmethod
    def get_instance():
        if BrennerLog.__instance is None:
            BrennerLog()
        return BrennerLog.__instance

    def __init__(self):
        if BrennerLog.__instance is not None:
            raise Exception("Singleton is already initialised.")
        else:
            self.src_dir = os.path.dirname(os.path.abspath(__file__))
            self.parent_dir = os.path.abspath(os.path.join(self.src_dir, '..'))
            self.log_folder = os.path.join(self.parent_dir, 'logs')
            self.bot_log_file = os.path.join(self.log_folder, 'bot.log')


            self.logger = logging.getLogger('brenner_log')
            self.logger.setLevel(logging.INFO)
            try:
                if not os.path.exists(self.log_folder):
                    print("Log folder not found. Creating a new folder...")
                    os.mkdir(self.log_folder)
                if not os.path.exists(self.bot_log_file):
                    print("Log file not found. Creating a new file...")
                    open(self.bot_log_file, 'a+').close()
                handler = logging.FileHandler(self.bot_log_file)
            except Exception as e:
                print(f"Error creating log file: {str(e)}")

            handler.setLevel(logging.INFO)
            # Set the log format
            formatter = logging.Formatter('%(asctime)s %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # Create singleton
            BrennerLog.__instance = self

    def write_log(self, user_id, command, full_command):
        # Log the user's command usage
        message = f'User {user_id} used command: {command} with full command: {full_command}'
        self.logger.info(message)

    def write_exception(self, exception):
        # Log the caught exception
        self.logger.exception(exception)


def log_command(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            if isinstance(args[1], Context):
                user = args[1].author.name
                full_command = args[1].message.content
            else:
                user = args[1].user.name
                full_command = args[1].data['options'][0]['value']
            BrennerLog.get_instance().write_log(user, func.__name__, full_command)
            return await func(*args, **kwargs)
        except Exception as e:
            BrennerLog.get_instance().write_exception(e)
            raise e
    return wrapper
