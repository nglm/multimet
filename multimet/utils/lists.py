from typing import List, Tuple, Any, Sequence, Iterable

def get_indices_element(
    my_list: List[Any],
    my_element: Any,
    all_indices: bool = True,
    if_none: Any = -1,
):
    """
    Return the first or all indices of an element

    :param my_list: List in which 'my_element' is searched
    :type my_list: List[Any]
    :param my_element: Element that is to be found
    :type my_element: Any
    :param all_indices: Return all indices?, defaults to True
    :type all_indices: bool, optional
    :param if_none: Return value if element not found, defaults to -1
    :type if_none: int, optional
    :return: Index of the element in the list
    :rtype: int if element found otherwise type(if_none)
    """
    if my_list is None:
        res = if_none
    indices = [i for i,x in enumerate(my_list) if x == my_element]
    res = indices
    # if my_element is not in the list
    if not indices:
        res = if_none
    # if we only want one index
    elif not all_indices:
        res = [indices[0]]
    return res  # List[int] or Type(if_none)
