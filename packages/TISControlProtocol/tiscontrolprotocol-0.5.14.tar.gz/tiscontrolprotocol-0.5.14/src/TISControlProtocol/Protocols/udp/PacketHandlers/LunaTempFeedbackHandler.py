from homeassistant.core import HomeAssistant
import logging


async def handle_luna_temp_feedback(hass: HomeAssistant, info: dict):
    """
    Handle the feedback from a Luna temperature sensor.
    """
    device_id = info["device_id"]
    temperature = int(info["additional_bytes"][1])

    event_data = {
        "device_id": device_id,
        "feedback_type": "temp_feedback",
        "additional_bytes": [temperature],
    }

    try:
        hass.bus.async_fire(str(info["device_id"]), event_data)
        # logging.error(
        #     f"control response event fired for {info['device_id']}, additional bytes: {info['additional_bytes']}"
        # )
    except Exception as e:
        logging.error(f"error in firing even for feedbackt: {e}")
