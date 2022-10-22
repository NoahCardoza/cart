from slugify import slugify


def slugify_listener(target, value, oldvalue, initiator):
    """Generate a slug from a SQLAlchemy model field.

    Args:
        target: The model instance that is being mutated.
        value (str): The new value od the field.
        oldvalue (str): The previous value of the field.
        initiator: Unused.
    """
    if value and (not target.slug or value != oldvalue):
        target.slug = slugify(value)
