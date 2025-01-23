# Home Assistant Add-on: Gazpar2HAWS add-on

## Configuration

The configuration permits to define multiple devices if you have multiple GrDF meters (meter1 and meter2 in the example above).

```yaml
scan_interval: 480
devices:
  - name: meter1
    username:
    password:
    pce_identifier:
    timezone: Europe/Paris
    last_days: 365
    reset: false
  - name: meter2
    username:
    password:
    pce_identifier:
    timezone: Europe/Paris
    last_days: 720
    reset: false
```

| Name                     | Description                                                                                                                                      | Required | Default value |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ------------- |
| scan_interval            | Period in minutes to refresh meter data (0 means one single refresh and stop)                                                                    | No       | 480 (8 hours) |
| devices[].name           | Name of the device in Home Assistant                                                                                                             | Yes      | -             |
| devices[].username       | GrDF account user name                                                                                                                           | Yes      | -             |
| devices[].password       | GrDF account password (avoid using special characters)                                                                                           | Yes      | -             |
| devices[].pce_identifier | GrDF meter PCE identifier                                                                                                                        | Yes      | -             |
| devices[].timezone       | Timezone of the GrDF data                                                                                                                        | No       | Europe/Paris  |
| devices[].last_days      | Number of days of history data to retrieve                                                                                                       | No       | 365 days      |
| devices[].reset          | Rebuild the history. If true, the data will be reset before the first data retrieval. If false, the data will be kept and new data will be added | No       | false         |
