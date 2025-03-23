from loguru import logger
from typing import Dict, Any

from dsmr_parser import telegram_specifications
from dsmr_parser.clients import SerialReader, SERIAL_SETTINGS_V5

from p1_influx_db.dsmr_parse import dsmrParse

from p1_influx_db.mqtt import Client


def mqttmain(config: Dict[str, Any]):
    logger.info("Opening SerialReader")
    mqtt_config = config["mqtt"]
    dsmrParser = dsmrParse(config["p1"])
    client = Client(**mqtt_config)
    client.start()
    serial_reader = SerialReader(
        device=config["p1"]["device"],
        serial_settings=SERIAL_SETTINGS_V5,
        telegram_specification=telegram_specifications.V5,
    )
    try:
        for telegram in serial_reader.read_as_object():
            info_list = dsmrParser.parse_dsmr_telegram(telegram)

            for dsmr_message in info_list:
                client.publish_messages(dsmr_message)
    except Exception as e:
        client.stop()
        logger.info("Closing MqttClient")
        raise e
