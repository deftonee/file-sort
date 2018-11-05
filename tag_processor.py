from typing import Text, Set

from enums import DEFAULT_FOLDER_NAME
from file_classes import File


class TagProcessor:
    """ Class transforms string with tags into folder name """
    tag_classes = {}

    @classmethod
    def process_string(
            cls, file_obj: File, string: Text, tags: Set[Text]) -> Text:
        result = string
        for tag in tags:
            if tag in cls.tag_classes:
                replacement = cls.tag_classes[tag].process(file_obj)
                result = result.replace(tag, replacement)
            else:
                result = DEFAULT_FOLDER_NAME
                break
        return result

    @classmethod
    def add_tag_class(cls, tag_cls):
        cls.tag_classes[tag_cls.tag] = tag_cls
