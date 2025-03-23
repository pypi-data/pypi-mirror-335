from loguru import logger
from typing import Dict, List, Any

from dsmr_parser.objects import Telegram

from collections import namedtuple
from pydantic import BaseModel, AwareDatetime


class p1Messages(BaseModel):
    measurement: str
    tags: Dict[str, Any]
    fields: Dict[str, Any]
    time: AwareDatetime


dsmrMessages = namedtuple("dsmrMessages", ["topic", "payload"])


class dsmrParse:
    def __init__(self, config):
        for key in config:
            if "keys" in config[key]:
                setattr(self, key, config[key]["keys"])

    def parse_dsmr_telegram(self, telegram: Telegram):
        """
        Parses a DSMR telegram and returns a list of dsmrMessages.

        Args:
            telegram (Telegram): The DSMR telegram to parse.

        Returns:
            list: A list of dsmrMessages containing the parsed data.

        """
        p1MessageList = []
        if hasattr(self, "electricity"):
            electricity_measurement = p1Messages(
                measurement="electricity",
                tags={
                    "unit": "kWh",
                    "equipment_id": telegram.EQUIPMENT_IDENTIFIER.value,
                },
                fields={},
                time=telegram.P1_MESSAGE_TIMESTAMP.value,
            )
            p1MessageList = self.fill_fields(
                telegram,
                self.electricity,
                electricity_measurement,
                p1MessageList,
                "kWh",
                "latest_energy",
            )
        if hasattr(self, "electricity_current"):
            electricity_flow = p1Messages(
                measurement="electricity_current",
                tags={
                    "unit": "kW",
                    "actief_tarief": telegram.ELECTRICITY_ACTIVE_TARIFF.value,
                    "equipment_id": telegram.EQUIPMENT_IDENTIFIER.value,
                },
                fields={},
                time=telegram.P1_MESSAGE_TIMESTAMP.value,
            )
            p1MessageList = self.fill_fields(
                telegram,
                self.electricity_current,
                electricity_flow,
                p1MessageList,
                "kW",
                "latest_energy_current",
            )
        if hasattr(self, "voltage"):
            voltages = p1Messages(
                measurement="voltage",
                tags={
                    "unit": "V",
                    "equipment_id": telegram.EQUIPMENT_IDENTIFIER.value,
                },
                fields={},
                time=telegram.P1_MESSAGE_TIMESTAMP.value,
            )
            p1MessageList = self.fill_fields(
                telegram,
                self.voltage,
                voltages,
                p1MessageList,
                "V",
                "latest_voltage_current",
            )
        if hasattr(self, "current"):
            currents = p1Messages(
                measurement="current",
                tags={
                    "unit": "A",
                    "equipment_id": telegram.EQUIPMENT_IDENTIFIER.value,
                },
                fields={},
                time=telegram.P1_MESSAGE_TIMESTAMP.value,
            )
            p1MessageList = self.fill_fields(
                telegram,
                self.current,
                currents,
                p1MessageList,
                "A",
                "latest_voltage_current",
            )

        if hasattr(self, "gas"):
            gas = p1Messages(
                measurement="gas",
                tags={
                    "unit": "m3",
                    "equipment_id": telegram.EQUIPMENT_IDENTIFIER_GAS.value,
                },
                fields={},
                time=telegram.P1_MESSAGE_TIMESTAMP.value,
            )
            p1MessageList = self.fill_fields(
                telegram,
                self.gas,
                gas,
                p1MessageList,
                "m3",
                "latest_gas",
            )
        return p1MessageList

    def fill_fields(
        self,
        parsed_telegram: Dict[str, any],
        keylist: List[str],
        message: p1Messages,
        p1MessageList: List[p1Messages],
        unitCheck: str,
        topic: str,
    ):
        """
        Fill the fields of the message with values from the parsed telegram.

        Args:
            parsed_telegram (Dict[str, any]): The parsed telegram containing key-value pairs.
            keylist (List[str]): The list of keys to be filled in the message fields.
            message (p1Messages): The message object to be filled.
            p1MessageList (List[p1Messages]): The list of message objects.

        Returns:
            List[p1Messages]: The updated list of message objects.
        """
        message = message.model_dump()
        for key in keylist:
            key = str.upper(key)
            if not hasattr(parsed_telegram, key):
                logger.debug("Key not in telegram")
                continue
            if getattr(parsed_telegram, key).unit != unitCheck:
                logger.critical(f"Unit is not {unitCheck}")
                return p1MessageList
            message["fields"][key.lower()] = float(getattr(parsed_telegram, key).value)
        if list(dict(message)["fields"].keys()):
            p1MessageList.append(dsmrMessages(topic=topic, payload=p1Messages(**message)))
        return p1MessageList
