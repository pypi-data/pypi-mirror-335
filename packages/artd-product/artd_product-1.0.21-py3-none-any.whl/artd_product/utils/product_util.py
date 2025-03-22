from artd_product.models import Category

categories_ids = []


def get_categories_tree(category_id=None, partner=None):
    categories_ids.clear()
    categories = None
    if partner is not None:
        categories = Category.objects.filter(partner=partner)
    else:
        categories = Category.objects.all()
    if category_id is not None:
        categories = categories.filter(id__gte=category_id)
    categories_tree = []
    for category in categories:
        if category.id not in categories_ids:
            categories_ids.append(category.id)
            category_tree = {
                "id": category.id,
                "text": category.name,
                "state": {
                    "opened": True,
                    "selected": False,
                },
                "children": get_children(category),
            }
            categories_tree.append(category_tree)
    return categories_tree


def get_children(category):
    children = Category.objects.filter(parent=category)
    children_tree = []
    for child in children:
        if child.id not in categories_ids:
            categories_ids.append(child.id)
            child_tree = {
                "id": child.id,
                "text": child.name,
                "state": {
                    "opened": True,
                    "selected": False,
                },
                "children": get_children(child),
            }
            children_tree.append(child_tree)
    return children_tree


def get_product_categories_tree(
    category_id=None,
    product_categories=None,
    disabled=False,
    partner=None,
):
    categories_ids.clear()
    if partner is not None:
        categories = Category.objects.filter(partner=partner)
    else:
        categories = Category.objects.filter(parent=None)
    if category_id is not None:
        categories = categories.filter(id__gte=category_id)
    categories_tree = []
    for category in categories:
        selected = False
        if category.id not in categories_ids:
            categories_ids.append(category.id)
            if category.id in product_categories:
                selected = True
            category_tree = {
                "id": category.id,
                "name": category.id,
                "text": category.name,
                "state": {
                    "opened": True,
                    "selected": selected,
                    "disabled": disabled,
                },
                "children": get_product_children(
                    category, product_categories, disabled=disabled
                ),
            }
            categories_tree.append(category_tree)
    for category in categories_tree:
        category["state"]["selected"] = True
        break
    return categories_tree


def get_product_children(category, product_categories=None, disabled=False):
    children = Category.objects.filter(parent=category)
    children_tree = []
    for child in children:
        selected = False
        if child.id in product_categories:
            selected = True
        if child.id not in categories_ids:
            categories_ids.append(child.id)
            child_tree = {
                "id": child.id,
                "text": child.name,
                "state": {
                    "opened": True,
                    "selected": selected,
                    "disabled": disabled,
                },
                "children": get_product_children(
                    child, product_categories, disabled=disabled
                ),
            }
            children_tree.append(child_tree)
    return children_tree
