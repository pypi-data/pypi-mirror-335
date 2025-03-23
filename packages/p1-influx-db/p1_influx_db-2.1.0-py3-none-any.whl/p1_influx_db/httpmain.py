from loguru import logger
import asyncio
from typing import Dict, Any

from p1_influx_db.dsmr_parse import dsmrParse
from dsmr_parser import telegram_specifications
from dsmr_parser.clients import AsyncSerialReader, SERIAL_SETTINGS_V5
from aiohttp.client_exceptions import ClientConnectorError


async def parse_telegram_influx(name, queue: asyncio.Queue, config_file: str, parser: dsmrParse):
    while True:
        telegram = await queue.get()
        info_list = parser.parse_dsmr_telegram(telegram)
        from .http_to_influxdb import send_parsed_telegram

        results = await send_parsed_telegram(info_list, queue, config_file)
        queue.task_done()


async def mainhttp(config: Dict[str, Any]):
    queue = asyncio.Queue()

    dsmrParser = dsmrParse(config["p1"])
    logger.info("Opening SerialReader")
    serial_reader = AsyncSerialReader(
        device=config["p1"]["device"],
        serial_settings=SERIAL_SETTINGS_V5,
        telegram_specification=telegram_specifications.V5,
    )
    tasks = []
    for i in range(3):
        tasks.append(
            asyncio.create_task(
                parse_telegram_influx(
                    f"worker-{i}",
                    queue,
                    config_file=config["p1"]["filepath"],
                    parser=dsmrParser,
                )
            )
        )

    await serial_reader.read_as_object(queue)
    result = await asyncio.gather(*tasks, return_exceptions=True)
    for r in result:
        if isinstance(r, ClientConnectorError):
            raise r
        elif isinstance(r, Exception):
            raise r
