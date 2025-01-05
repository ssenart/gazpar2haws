# Home Assistant Add-on: Gazpar2HAWS add-on

## Configuration

```yaml
grdf:
    scan_interval: 480
    username:
    password:
    pce_identifier:
    timezone: Europe/Paris
    last_days: 365
    reset: false 
```

| Name | Description | Required | Default value |
|---|---|---|---|
| grdf.scan_interval  |  Period in minutes to refresh meter data (0 means one single refresh and stop)  | No | 480 (8 hours) |
| grdf.username  |  GrDF account user name | Yes | - |
| grdf.password  | GrDF account password (avoid using special characters)  | Yes | - |
| grdf.pce_identifier  | GrDF meter PCE identifier | Yes | - |
| grdf.timezone | Timezone of the GrDF data | No | Europe/Paris |
| grdf.last_days  | Number of days of history data to retrieve  | No | 365 days |
| grdf.reset  | Rebuild the history. If true, the data will be reset before the first data retrieval. If false, the data will be kept and new data will be added  | No | false |
