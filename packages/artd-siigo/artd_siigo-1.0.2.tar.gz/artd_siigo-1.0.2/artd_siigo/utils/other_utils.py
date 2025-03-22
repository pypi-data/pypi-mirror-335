from typing import Any, Dict
from django.db import models
from django.forms.models import model_to_dict


def model_to_dict_custom(instance: models.Model) -> Dict[str, Any]:
    """
    Converts a Django model instance into a dictionary, including ForeignKey and
    ManyToManyField relationships as nested dictionaries or lists of dictionaries.
    Handles ImageField fields by including their URLs instead of file references.

    Args:
        instance (models.Model): The model instance to convert to a dictionary.

    Returns:
        Dict[str, Any]: A dictionary representation of the model instance, with
        ForeignKey fields as dictionaries, ManyToManyField fields as lists of dictionaries,
        and ImageField fields as URLs.
    """
    # Convert simple fields to dictionary
    data = model_to_dict(instance)

    # Process each field in the model instance
    for field in instance._meta.fields:
        if isinstance(field, models.ForeignKey):
            related_instance = getattr(instance, field.name)
            if related_instance is not None:
                # Convert ForeignKey instance to dictionary
                data[field.name] = model_to_dict_custom(related_instance)

        elif isinstance(field, models.ImageField):
            # Handle ImageField by getting the URL of the file
            image_file = getattr(instance, field.name)
            data[field.name] = image_file.url if image_file else None

    # Process ManyToMany fields
    for field in instance._meta.many_to_many:
        related_queryset = getattr(instance, field.name).all()
        # Convert each related instance to a dictionary
        data[field.name] = [
            model_to_dict_custom(related_instance)
            for related_instance in related_queryset
        ]

    return data
