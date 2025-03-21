# Define monitoring payload types
payload_types = {
    "Env": {
        "temp_air": float,
        "temp_water": float,
        "rel_hum": float,
        "dp": float,
        "can_errors": int,
        "i2c_errors": int,
        "runtime": int,
        "valve0_status": int,
        "valve1_status": int,
    },
    "VAR": {
        "green": int,  # 1 means on
        "yellow": int,  # 1 means on
        "red": int,  # 1 means on
        "lid_status": int,  # 1 means locked, otherwise open
        "interlock_status": int,  # 1 means good, otherwise bad
        "free_disk_space": int,  # value in GB
        "flowswitch_status": int,  # < 0 means not implemented, 0 means bad, otherwise good
        "throttle": int,
    },
    'Supply_U': [float] * 8,
    'Supply_P': [float] * 8,
    'Supply_I': [float] * 8,
    'Peltier_U': [float] * 8,
    'Peltier_P': [float] * 8,
    'Peltier_I': [float] * 8,
    'Peltier_R': [float] * 8,
    'ControlVoltage_Set': [float] * 8,
    'Error': [int] * 8,  # TEC controller errors in hex format (leading '0x')
    'Mode': [int] * 8,
    'Temp_Diff': [float] * 8,
    'Temp_M': [float] * 8,
    'Temp_Set': [float] * 8,
    'Temp_W': [float] * 8,
    'PID_Max': [float] * 8,
    'PID_Min': [float] * 8,
    'PID_kd': [float] * 8,
    'PID_ki': [float] * 8,
    'PID_kp': [float] * 8,
    'PowerState': [int] * 8,
    'Ref_U': [float] * 8,
}
