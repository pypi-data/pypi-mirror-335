from enum import Enum


class ListEmailCategoriesName(str, Enum):
    CATEGORYFORUMS = "CATEGORY_FORUMS"
    CATEGORYPERSONAL = "CATEGORY_PERSONAL"
    CATEGORYPROMOTIONS = "CATEGORY_PROMOTIONS"
    CATEGORYSOCIAL = "CATEGORY_SOCIAL"
    CATEGORYUPDATES = "CATEGORY_UPDATES"

    def __str__(self) -> str:
        return str(self.value)
