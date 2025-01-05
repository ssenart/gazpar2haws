# Home Assistant Add-on: Gazpar2HAWS add-on

## Configuration

```yaml
grdf:
    scan_interval: 480 # Number of minutes between each data retrieval (0 means no scan: a single data retrieval at startup, then stops).
    username: # GrDF account user name.
    password: # GrDF account password.
    pce_identifier: # GrDF account PCE identifier.
    timezone: Europe/Paris # Timezone of the HA instance.
    last_days: 365 # Number of days of data to retrieve.
    reset: false # Rebuild the history. If true, the data will be reset before the first data retrieval. If false, the data will be kept and new data will be added.
```
