from enum import Enum


class ListEmailCategoriesArrayItemRefCategoryId(str, Enum):
    CATEGORY_FORUMS = "CATEGORY_FORUMS"
    CATEGORY_PERSONAL = "CATEGORY_PERSONAL"
    CATEGORY_PROMOTIONS = "CATEGORY_PROMOTIONS"
    CATEGORY_SOCIAL = "CATEGORY_SOCIAL"
    CATEGORY_UPDATES = "CATEGORY_UPDATES"

    def __str__(self) -> str:
        return str(self.value)
