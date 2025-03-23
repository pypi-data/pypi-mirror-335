# p1-influx-db
A python implementation for pushing data to influxDB from a P1 meter

This packages uses the HTTP api from influxDB to store the given data of the P1 meter
The package contains a python module named p1_influx_db which requires a path towards the config as input. An example config can be found in the package.
This config is a toml which let's the module know what kind of behaviour you want to use. In order to process the DSMR p1 information the config requires a [p1] clause. Depending on the method of transmission either a [influx2] block or a [mqtt] block. Both are valid protocols for transmitting the data.
The keys are the given fields that you want to receive data on; these can be changed depending on the type of meter available and the interest in the values.

## Getting started

To start the module just use `python -m p1_influx_db --config <path_to_config>`

For which the following is an example config:
```toml
# TOML-based config
[influx2]
url = "http://localhost:8086"
org = "my-org"
token = "my-token"

[mqtt]
broker = "localhost"
port = 433
client_id = "client_id"
ca_certs = "/etc/certificate/abc"
certfile = "/etc/certificate/abc"
key = "etc/certificate/key"

[p1]
device = "/dev/serial0"

[p1.electricity]
keys = ["ELECTRICITY_USED_TARIFF_1",
        "ELECTRICITY_USED_TARIFF_2",
        "ELECTRICITY_DELIVERED_TARIFF_1",
        "ELECTRICITY_DELIVERED_TARIFF_2"]

[p1.electricity_current]
keys = ["CURRENT_ELECTRICITY_USAGE",
        "CURRENT_ELECTRICITY_DELIVERY",
        "INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE",
        "INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE",
        "INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE",
        "INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE",
        "INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE",
        "INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE"]

[p1.voltage]
keys = ["INSTANTANEOUS_VOLTAGE_L1",
        "INSTANTANEOUS_VOLTAGE_L2",
        "INSTANTANEOUS_VOLTAGE_L3"]

[p1.current]
keys = ["INSTANTANEOUS_CURRENT_L1",
        "INSTANTANEOUS_CURRENT_L2",
        "INSTANTANEOUS_CURRENT_L3"]

[p1.gas]
keys = ["HOURLY_GAS_METER_READING"]
```

## Instalation

The package has multiple modes of installation namely full, influxdb or mqtt. In other to save space it is advised to use the extra install fields just for the protocol required so either.
`pip install p1-influx-db[mqtt]` or `pip install p1-influx-db[influxdb]`