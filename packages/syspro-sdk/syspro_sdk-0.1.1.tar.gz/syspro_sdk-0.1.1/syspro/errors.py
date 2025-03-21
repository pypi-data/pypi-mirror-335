
def validate_attributes(attributes):
    for attr_name, attr_value in attributes.items():
        if attr_value is None:
            raise ValueError(f"{attr_name.replace('_', ' ').capitalize()} is not set.")

def validate_syspro_response(response):
    """
    Check if the Syspro response contains an Error event with a 200 response.

    :param response: Syspro response object.
    :return: True if an Error event is found, False otherwise.
    """
    if response.status_code == 200:
        data = response.read().decode("utf-8").upper().split()
        if data[0] =="ERROR":
            raise ValueError(f"Syspro Error: {data}")
    return False
