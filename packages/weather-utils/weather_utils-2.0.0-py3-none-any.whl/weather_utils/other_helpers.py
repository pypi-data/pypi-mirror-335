from decimal import Decimal

def convert_decimal(obj):
    """ Recursively convert Decimal objects to int or float. """
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)  # Convert to int if whole number, else float
    elif isinstance(obj, list):
        return [convert_decimal(item) for item in obj]  # Convert list items
    elif isinstance(obj, dict):
        return {key: convert_decimal(value) for key, value in obj.items()}  # Convert dict values
    return obj
