from typing import Any
import os


class BotMessages:
    _instance = None
    _is_initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BotMessages, cls).__new__(cls)
        return cls._instance


    def __init__(self, messages_dir: str='messages/'):
        if not self._is_initialized:
            self.messages_dir = messages_dir
            self.load_all_messages()
            self._is_initialized = True


    def load_all_messages(self):
        for filename in os.listdir(self.messages_dir):
            if filename.endswith('.txt'):
                # Remove the .txt extension and use the rest as the attribute name
                attr_name = filename[:-4]
                with open(os.path.join(self.messages_dir, filename), 'r', encoding='utf-8') as file:
                    setattr(self, attr_name, file.read())
