from tessie_relay.psi_coldbox import Coldbox
from time import sleep

def handle_error_message(error_payload):
    """
    Custom callback to handle "Error" messages.
    :param error_payload: The parsed "Error" payload
    """
    print("WARNING: Error detected!")
    print(error_payload)


if __name__ == "__main__":

    # initialize the Coldbox controller and provide a callback for alarms
    coldbox = Coldbox(host='coldbox02.psi.ch', error_callback=handle_error_message)

    with coldbox:
        coldbox.flush()
        print("air temperature    ", coldbox.get_air_temperature())
        print("water temperature  ", coldbox.get_water_temperature())
        print("interlock status   ", coldbox.get_interlock_status(timeout=10))
        print("traffic light      ", coldbox.get_traffic_light())
        print("flow switch        ", coldbox.get_flow_switch())
        print("lid                ", coldbox.get_lid_status())
        channel = 8
        print(f"voltage probes for channel {channel} = ", coldbox.get_voltage_probe(channel)) 

        try:
            while True:
                print("relative humidity ", coldbox.get_relative_humidity())
                sleep(10)
        except KeyboardInterrupt:
            print('interrupted!')

    print("shutting down")
