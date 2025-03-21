# Local import
from .payload_types import payload_types


# General conversion function
def convert_payload(payload):
    # First, catch alarms
    if payload.startswith("==ALARM=="):
        return {"Alarm": payload[10:]}

    payload_type, payload_data = payload.split("=", 1)
    payload_type = payload_type.strip()

    if payload_type not in payload_types:
        raise ValueError(f"Unknown payload type: {payload_type}")

    # Split data by comma and strip whitespace
    payload_list = [x.strip() for x in payload_data.split(",")]

    if payload_type == "VAR":
        # Special parsing for 'VAR' payload
        payload_dict = {}
        for key, value in zip(payload_types["VAR"], payload_list):
            if value.startswith(('G', 'Y', 'R', 'L', 'I', 'D', 'F', 'T')):
                # Extract numeric part from strings like 'G0', 'Y1'
                # Handle traffic light
                if value.startswith(('G', 'Y', 'R')):
                    payload_dict[key] = "off"
                    if int(value[1:]) == 1:
                        payload_dict[key] = "on"
                # Handle lid sensor
                elif value.startswith('L'):
                    payload_dict[key] = "open"
                    if int(value[1:]) == 1:
                        payload_dict[key] = "locked"
                # Handle interlock status
                elif value.startswith('I'):
                    payload_dict[key] = "bad"
                    if int(value[1:]) == 1:
                        payload_dict[key] = "good"
                elif value.startswith('F'):
                    payload_dict[key] = "bad"
                    if int(value[1:]) < 0:
                        payload_dict[key] = "not implemented"
                    elif int(value[1:]) > 0:
                        payload_dict[key] = "good"
                else:
                    payload_dict[key] = int(value[1:])
            else:
                payload_dict[key] = int(value)
        return {"VAR": payload_dict}

    elif payload_type == "Env":
        # Convert to dictionary for 'Env' type
        payload_dict = dict(zip(payload_types["Env"], payload_list))
        for key, value in payload_dict.items():
            payload_dict[key] = payload_types["Env"][key](value) if value.lower() != "nan" else None
        return {"Env": payload_dict}

    elif payload_type == "Error":
        # Error returns hex values, convert to integers
        return {payload_type: [payload_types[payload_type][i](value, 16) if value.lower() != "nan" else None for i, value in enumerate(payload_list)]}
    
    elif isinstance(payload_types[payload_type], list):
        # General handling for list-based payloads (e.g., 'Peltier_U', 'Peltier_R', etc.)
        return {payload_type: [payload_types[payload_type][i](value) if value.lower() != "nan" else None for i, value in enumerate(payload_list)]}

    raise ValueError(f"Unhandled payload type: {payload_type}")
