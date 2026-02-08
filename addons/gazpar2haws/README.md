# Home Assistant Add-on: Gazpar2HAWS

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg

**Supported Architectures**: This add-on supports modern 64-bit architectures (aarch64, amd64) as required by current Home Assistant versions. Legacy 32-bit architectures (armhf, armv7, i386) are no longer supported by Home Assistant.

## About

Gazpar2HAWS is a Home Assistant add-on that reads gas consumption data history from GrDF (French gas provider) meters and publishes it to Home Assistant as cumulative statistics, compatible with the Home Assistant Energy Dashboard.

### Key Features

- 📊 **Historical data retrieval**: Import up to 3 years of historical gas consumption data
- 💰 **Detailed cost breakdown**: Calculate and track consumption, subscription, transport, and tax costs
- 📈 **Energy Dashboard compatible**: Seamlessly integrates with Home Assistant's Energy Dashboard
- ⚙️ **Flexible pricing**: Support for complex pricing models with multiple VAT rates, time-based and quantity-based pricing
- 🔄 **Automatic updates**: Periodically retrieves new meter readings from GrDF
- 📱 **Multiple devices**: Configure multiple GrDF meters in a single instance

## Documentation

- **[📖 Full Documentation](https://github.com/ssenart/gazpar2haws/blob/main/addons/gazpar2haws/DOCS.md)** - Complete configuration guide and pricing examples
- **[⚙️ Installation Guide](https://github.com/ssenart/gazpar2haws/blob/main/README.md#installation)** - How to install and configure the add-on
- **[🔄 Migration Guide](https://github.com/ssenart/gazpar2haws/blob/main/MIGRATIONS.md)** - If upgrading from v0.3.x (breaking changes in v0.4.0)
- **[❓ FAQ](https://github.com/ssenart/gazpar2haws/blob/main/docs/FAQ.md)** - Common questions and troubleshooting

## Quick Start

1. Add the repository to Home Assistant: `https://github.com/ssenart/gazpar2haws`
2. Install the Gazpar2HAWS add-on from the add-on store
3. Configure with your GrDF credentials and Home Assistant token
4. Start the add-on
5. View published entities in Home Assistant (sensor.{name}_volume, sensor.{name}_energy, etc.)

## Configuration

The add-on requires:
- GrDF username and password
- GrDF meter PCE identifier (quoted in configuration to preserve leading zeros)
- Home Assistant access token

Optional pricing configuration enables cost calculations for consumption, subscription, transport, and energy taxes.

**See [DOCS.md](https://github.com/ssenart/gazpar2haws/blob/main/addons/gazpar2haws/DOCS.md)** for detailed configuration examples.

## Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/ssenart/gazpar2haws/issues)
- **Questions**: Ask in [GitHub Discussions](https://github.com/ssenart/gazpar2haws/discussions)
- **Project**: [GitHub Repository](https://github.com/ssenart/gazpar2haws)