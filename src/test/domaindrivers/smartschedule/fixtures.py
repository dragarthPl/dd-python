from typing import Any


def contains_only_once_elements_of(to_check_list: list[Any], expected_only_once_list: list[Any]) -> bool:
    element_count: dict[Any, Any] = {}
    for elem in expected_only_once_list:
        element_count[elem] = element_count.get(elem, 0) + 1

    for elem in to_check_list:
        how_many = element_count.get(elem, 0)
        for key in element_count:
            if key == elem:
                how_many -= 1
        if how_many != 0:
            return False

    return True
