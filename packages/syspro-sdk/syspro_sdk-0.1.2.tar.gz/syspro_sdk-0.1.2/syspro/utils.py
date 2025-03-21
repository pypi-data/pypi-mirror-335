import xml.etree.ElementTree as ET
from datetime import datetime

def get_nested(data, keys):
    """Retrieve data from nested dictionaries using a list of keys."""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            print(f"Key '{key}' not found in the data, return empty data")
            data = None
    return data

def clean_values(data, types_map):
    for key, value in data. items():
        if key in types_map:
            try:
                data[key] = types_map[key](value)
            except ValueError:
                pass
    return data

def serialize_to_xml(data: dict, root_tag: str = "Query") -> str:
    """
    Serialize dictionary data to XML format, handling None values as self-closing tags.

    :param data: Dictionary to serialize.
    :param root_tag: Root tag name for the XML.
    :return: Serialized XML string.
    """
    def build_element(parent, key, value):
        if isinstance(value, dict):
            # Check for attributes
            attributes = value.get("@attributes", {})
            elem = ET.SubElement(parent, key, attrib=attributes)
            for k, v in value.items():
                if k != "@attributes":  # Skip attributes when building child elements
                    build_element(elem, k, v)
        elif isinstance(value, list):
            # Lists create multiple elements with the same tag
            for item in value:
                build_element(parent, key, item)
        elif value is None:
            # Self-closing tag for None values
            ET.SubElement(parent, key)
        else:
            # Scalar values
            elem = ET.SubElement(parent, key)
            elem.text = str(value)

    # Extract root attributes if present
    root_attributes = data.pop("@attributes", {})
    root = ET.Element(root_tag, attrib=root_attributes)

    for k, v in data.items():
        build_element(root, k, v)

    return ET.tostring(root, encoding="unicode", method="xml")

def clean_field(data: dict, field_name: str, default_value: str) -> dict:
    """
    Recursively traverse the dictionary and update the specified field with a default value
    if it is missing or invalid.

    :param data: The input dictionary to clean.
    :param field_name: The field name to clean (e.g., "PriceValidFrom").
    :param default_value: The default value to set if the field is missing or invalid.
    :return: The cleaned dictionary.
    """
    for key, value in data.items():
        if isinstance(value, dict):
            # Recursive call for nested dictionaries
            clean_field(value, field_name, default_value)
        elif isinstance(value, list):
            # Process lists of dictionaries
            for item in value:
                if isinstance(item, dict):
                    clean_field(item, field_name, default_value)
        elif key == field_name and (not value or value == ""):
            # Replace missing or invalid field value
            data[key] = default_value
    return data

def find_operator(operator: str):
        if operator == "==":
            return "EQ"
        elif operator == "!=":
            return "NE"
        elif operator == ">":
            return "GT"
        elif operator == "<":
            return "LT"
        elif operator == ">=":
            return "GE"
        elif operator == "<=":
            return "LE"
        elif operator == "contains":
            return "LIKE"
        elif operator == "startswith":
            return "LIKE"
        else:
            raise ValueError(f"Unsupported operator: {operator}")

def filter_json(json_data, filter_conditions):
    """
    Filters a list of JSON objects based on nested logical conditions ("AND"/"OR").

    Args:
        json_data (list of dict): List of JSON objects to filter.
        filter_conditions (dict): A dictionary defining nested filter conditions with "AND"/"OR".

    Returns:
        list: A list of matching JSON objects.
    """
    def parse_date(value):
        """Attempt to parse a value as a date in the format YYYY-MM-DD."""
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None
    
    def parse_number(value):
        """Attempt to parse a value as a float or int."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def parser(actual_value, expected_value):
        # Detect if either value is a date
        actual_date = parse_date(actual_value)
        expected_date = parse_date(expected_value)

        if actual_date and expected_date:
            # Both values are dates, perform date comparison
            actual_value, expected_value = actual_date, expected_date
        else:
            # Otherwise, try to treat them as numbers
            actual_number = parse_number(actual_value)
            expected_number = parse_number(expected_value)
            if actual_number is not None and expected_number is not None:
                actual_value, expected_value = actual_number, expected_number

        return actual_value, expected_value

    def apply_operator(actual_value, operator, expected_value):
        # Detect if either value is a date
        actual_value, expected_value = parser(actual_value, expected_value)
        # Perform comparison
        if operator == "==":
            return actual_value == expected_value
        elif operator == "!=":
            return actual_value != expected_value
        elif operator == ">":
            return actual_value > expected_value
        elif operator == "<":
            return actual_value < expected_value
        elif operator == ">=":
            return actual_value >= expected_value
        elif operator == "<=":
            return actual_value <= expected_value
        elif operator == "contains":
            return expected_value in str(actual_value)
        elif operator == "startswith":
            return str(actual_value).startswith(str(expected_value))
        elif operator == "endswith":
            return str(actual_value).endswith(str(expected_value))
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def get_value_from_path(obj, path):
        """Retrieve a value from a dictionary using a dotted path."""
        keys = path.split(".")
        for key in keys:
            obj = obj.get(key, None)
            if obj is None:
                break
        return obj

    def evaluate_condition(item, condition):
        """Recursively evaluates conditions with AND/OR logic."""
        if isinstance(condition, dict):
            if "AND" in condition:
                return all(evaluate_condition(item, sub_condition) for sub_condition in condition["AND"])
            elif "OR" in condition:
                return any(evaluate_condition(item, sub_condition) for sub_condition in condition["OR"])
        elif isinstance(condition, list):
            path, operator, value = condition
            actual_value = get_value_from_path(item, path)
            return apply_operator(actual_value, operator, value)
        else:
            raise ValueError(f"Invalid condition format: {condition}")

    # Filter the JSON data
    matching_items = [item for item in json_data if evaluate_condition(item, filter_conditions)]

    return matching_items

def flatten_json(data, parent_key, nested_key):
    """
    Flattens a JSON structure by moving nested elements (using dotted paths) to the top level
    and merging specified parent-level data into each nested element.

    Args:
        data (list or dict): Input JSON data.
        parent_key (str): The key indicating the parent-level data to merge.
        nested_key (str): The dotted path key containing the nested elements to flatten.

    Returns:
        list: Flattened list of dictionaries with combined parent and nested data.
    """
    def ensure_list(value):
        """Ensure the value is always a list."""
        if isinstance(value, dict):
            return [value]
        elif isinstance(value, list):
            return value
        else:
            raise ValueError("Expected a dict or list for nested data.")

    def get_nested_value(obj, dotted_path):
        """Retrieve a nested value from a dictionary using a dotted path."""
        keys = dotted_path.split(".")
        for key in keys:
            obj = obj.get(key, {})
            if obj is None:
                break
        return obj

    if isinstance(data, dict):
        data = [data]

    flattened = []
    for item in data:
        # Extract the parent-level data and resolve the nested items using the dotted path
        parent_data = item.get(parent_key, {})
        nested_items = ensure_list(get_nested_value(item, nested_key))
        
        # Combine each nested item with parent-level data
        for nested_item in nested_items:
            combined = {**nested_item, **parent_data}
            flattened.append(combined)
    
    return flattened

