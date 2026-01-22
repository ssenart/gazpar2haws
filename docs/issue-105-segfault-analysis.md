# Issue #105: Segmentation Fault Analysis

## Issue Summary

**Issue**: [#105 - L'add-on ne démarre pas (exit code 139)](https://github.com/ssenart/gazpar2haws/issues/105)

**Symptom**: Multiple users reported that the Gazpar2HAWS Home Assistant add-on crashes with a segmentation fault (exit code 139) during startup after updating to Home Assistant 2026.1.x.

**Error Message**:
```
Segmentation fault (core dumped) python3 -m gazpar2haws --config config/configuration.yaml --secrets config/secrets.yaml
Halt add-on with exit code 139
```

**Affected Versions**:
- Home Assistant 2026.1.1 and 2026.1.2
- Gazpar2HAWS 0.4.0

## Root Cause Analysis

### 1. Home Assistant 2026.1 Changes

Home Assistant 2026.1 introduced significant infrastructure changes:
- **Python version**: Upgraded from Python 3.12 to Python 3.13.2+ (required minimum)
- **Docker base images**: Bumped to version 2025.12.0 with Python 3.13.11 and 3.14.2
- **Reference**: [Home Assistant 2026.1 Release](https://www.home-assistant.io/blog/2026/01/07/release-20261/)

### 2. Pydantic + Alpine Linux Compatibility Issue

The segmentation fault is caused by a **known incompatibility between pydantic-core and Alpine Linux with musl libc**.

**Key Technical Details**:

1. **Current Add-on Configuration**:
   - Gazpar2HAWS uses Alpine-based Docker images (see `addons/gazpar2haws/build.yaml`)
   - Base images: `ghcr.io/home-assistant/*/base-python:3.12-alpine3.20`
   - Alpine uses musl libc instead of glibc

2. **Pydantic Dependencies**:
   - Current: `pydantic[email] (>=2.10.6,<3.0.0)` and `pydantic-extra-types (>=2.10.2,<3.0.0)`
   - pydantic-core is a Rust-based extension that requires compiled binaries
   - **Critical Issue**: pydantic-core does not ship pre-built wheels for certain musl/Alpine combinations

3. **Documented Upstream Issues**:
   - [pydantic-core #1721](https://github.com/pydantic/pydantic-core/issues/1721): "Install crashes on ARM with Musl (e.g. RPi + Alpine)"
   - [pydantic-core #451](https://github.com/pydantic/pydantic-core/issues/451): Segmentation faults tracking issue
   - [pydantic #4230](https://github.com/pydantic/pydantic/discussions/4230): "Pydantic v2, Rust, and Alpine Linux"

### 3. Why It Manifested in HA 2026.1

The issue was triggered when:
1. Home Assistant 2026.1 updated the base container environment
2. The Alpine + musl combination exposed latent compatibility issues in pydantic-core
3. Python 3.13 compatibility compounded the issue (pydantic < 2.8.0 incompatible with Python 3.13)

**Quote from pydantic-core #1721**:
> "Installation of pydantic-core>=2.0.0 crashes on ARM platforms with Musl libc linux running as the kernel. Pydantic does not ship a py wheel of pydantic-core for cpython-312-arm-linux-musleabihf."

## Solution

### Recommended Fix: Switch to Debian-based Images

Replace Alpine Linux base images with Debian-based equivalents to avoid musl libc compatibility issues.

**Change in `addons/gazpar2haws/build.yaml`**:

```yaml
# FROM (Alpine - problematic):
build_from:
  aarch64: ghcr.io/home-assistant/aarch64-base-python:3.12-alpine3.20
  amd64: ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.20
  # ... other architectures

# TO (Debian - compatible):
build_from:
  aarch64: ghcr.io/home-assistant/aarch64-base-python:3.13-debian12
  amd64: ghcr.io/home-assistant/amd64-base-python:3.13-debian12
  # ... other architectures
```

### Benefits of Debian-based Images

1. **Compatibility**: Uses glibc instead of musl, fully compatible with pydantic-core
2. **Python 3.13 Support**: Matches Home Assistant 2026.1 requirements
3. **Pre-built Wheels**: pydantic-core ships manylinux wheels for Debian/glibc platforms
4. **Stability**: Widely used and tested in the Home Assistant ecosystem

### Alternative Considerations

**Why not stay on Alpine?**
- Missing pre-built wheels means compilation from source
- Rust toolchain complications on Alpine/musl
- Ongoing segfault risks with pydantic-core updates

**Why not pin older HA versions?**
- Users expect add-ons to work with latest HA
- Security updates in newer HA versions
- Feature improvements and bug fixes

## Impact Assessment

**User Impact**:
- HIGH: Add-on completely non-functional on HA 2026.1.x
- Multiple user reports in issue #105

**Migration Risk**:
- LOW: Debian images are officially supported by Home Assistant
- Image size slightly larger (~50-100MB more) but acceptable for add-ons
- No code changes required, only base image swap

**Testing Required**:
- Verify add-on starts successfully on all architectures
- Confirm data persistence across image change
- Test on HA 2026.1.x and verify backward compatibility with HA 2025.x

## Timeline

- **Issue Reported**: January 2026 (by @Dridrinou and @iWils)
- **Root Cause Identified**: January 22, 2026
- **Fix Implementation**: January 22, 2026
- **Target Release**: 0.5.0

## References

- [Issue #105](https://github.com/ssenart/gazpar2haws/issues/105)
- [Discussion #100](https://github.com/ssenart/gazpar2haws/discussions/100)
- [pydantic-core #1721 - ARM + musl crash](https://github.com/pydantic/pydantic-core/issues/1721)
- [pydantic #4230 - v2, Rust, and Alpine Linux](https://github.com/pydantic/pydantic/discussions/4230)
- [Home Assistant 2026.1 Release Notes](https://www.home-assistant.io/blog/2026/01/07/release-20261/)
- [Home Assistant Docker Base Releases](https://github.com/home-assistant/docker-base/releases)
