from django.core.exceptions import ValidationError


def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.SC2Replay']
    if not ext in valid_extensions:
        raise ValidationError('Unsupported File Extension. Please Upload a Replay Ending In .SC2Replay')

