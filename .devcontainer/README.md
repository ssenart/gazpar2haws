# Gazpar2HAWS DevContainer Guide

This devcontainer provides a complete Home Assistant development environment for testing the Gazpar2HAWS add-on locally. No manual setup required - everything runs in an isolated Docker container.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Step-by-Step Guide](#step-by-step-guide)
- [Accessing Home Assistant](#accessing-home-assistant)
- [Testing the Add-on](#testing-the-addon)
- [Troubleshooting](#troubleshooting)
- [Cleanup](#cleanup)

## Prerequisites

Before you begin, make sure you have:

1. **Docker Desktop** (or Docker Engine)
   - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Ensure Docker is running before proceeding
   - Verify: `docker --version`

2. **Visual Studio Code**
   - [Download VS Code](https://code.visualstudio.com/)

3. **Dev Containers Extension**
   - Install from VS Code Marketplace
   - Or run: `code --install-extension ms-vscode-remote.remote-containers`

## Quick Start

```bash
# 1. Open the project in VS Code
code /path/to/gazpar2haws

# 2. When prompted, click "Reopen in Container"
# Or press F1 → "Dev Containers: Reopen in Container"

# 3. Wait for container to build (first time takes 5-10 minutes)

# 4. Once inside container, run this task:
# Terminal → Run Task → Start Home Assistant

# 5. Access Home Assistant at:
# http://localhost:7123
```

## Step-by-Step Guide

### Step 1: Open Project in VS Code

```bash
cd /path/to/gazpar2haws
code .
```

### Step 2: Reopen in Container

You have three options:

**Option A - Popup Notification:**
- When you open the project, VS Code detects the `.devcontainer` folder
- Click the popup: **"Reopen in Container"**

**Option B - Command Palette:**
- Press `F1` (or `Ctrl+Shift+P` / `Cmd+Shift+P`)
- Type: `Dev Containers: Reopen in Container`
- Press Enter

**Option C - Status Bar:**
- Click the green button in the **bottom-left corner** of VS Code
- Select: `Reopen in Container`

### Step 3: Wait for Build

The first time you open the devcontainer:
- Docker pulls the `ghcr.io/home-assistant/devcontainer:2-addons` image (~2-5 minutes)
- VS Code sets up extensions and environment (~1-2 minutes)
- You'll see build progress in a terminal window

**Total time: 5-10 minutes for first build**

Subsequent starts are much faster (30-60 seconds).

### Step 4: Verify Container is Running

Once the build completes, you should see:
- ✅ Green indicator in bottom-left corner showing **"Dev Container: Example devcontainer for add-on repositories"**
- ✅ Terminal opens automatically with bash prompt
- ✅ Extensions loaded (ShellCheck, Prettier)

### Step 5: Start Home Assistant

Now that you're inside the container, start Home Assistant:

**Option A - Using VS Code Task (Recommended):**
1. Click **Terminal** menu → **Run Task...**
2. Select: **"Start Home Assistant"**
3. A new terminal opens and runs `supervisor_run`

**Option B - Manual Command:**
```bash
supervisor_run
```

**What happens:**
- Supervisor starts (takes ~30-60 seconds)
- Home Assistant initializes (takes ~2-3 minutes first time)
- The add-on is automatically detected in `/addons/local/`

**You'll see output like:**
```
[INFO] Starting Supervisor...
[INFO] Supervisor is running...
[INFO] Starting Home Assistant...
```

**Wait until you see:**
```
[INFO] Home Assistant is running
```

### Step 6: Access Home Assistant

Once Home Assistant is running, open your browser:

**Home Assistant Web UI:**
```
http://localhost:7123
```

**First-time setup:**
1. Complete the onboarding wizard
2. Create your admin account
3. Set up your location and preferences

**Port Mappings:**
- `7123` → Home Assistant Web UI (port 8123 inside container)
- `7357` → Supervisor API (port 4357 inside container)

## Accessing Home Assistant

### Web Interface

Navigate to: **http://localhost:7123**

### Finding Your Add-on

1. Click **Settings** in the sidebar
2. Click **Add-ons** (or **Apps** in newer versions)
3. Look for **Local add-ons** section
4. You should see **Gazpar2HAWS** listed there

### Installing the Add-on

1. Click on **Gazpar2HAWS** in Local add-ons
2. Click **Install**
3. Wait for installation to complete
4. Click **Configuration** tab
5. Add your GrDF credentials and settings
6. Click **Save**
7. Click **Start**

## Testing the Add-on

### View Add-on Logs

**Via Home Assistant UI:**
1. Settings → Add-ons → Gazpar2HAWS
2. Click **Log** tab
3. Logs update in real-time

**Via Command Line (in VS Code terminal):**
```bash
ha addon logs gazpar2haws
```

**Follow logs in real-time:**
```bash
ha addon logs gazpar2haws --follow
```

### Restart Add-on After Code Changes

Whenever you modify the code, restart the add-on:

**Via Home Assistant UI:**
1. Settings → Add-ons → Gazpar2HAWS
2. Click **Restart**

**Via Command Line:**
```bash
ha addon restart gazpar2haws
```

### Check Add-on Status

```bash
# View add-on info
ha addon info gazpar2haws

# View add-on configuration
ha addon config gazpar2haws

# List all add-ons
ha addon list
```

### Verify Entities Created

1. Go to **Settings** → **Devices & Services** → **Entities**
2. Search for: `gazpar2haws`
3. You should see entities like:
   - `sensor.gazpar2haws_volume`
   - `sensor.gazpar2haws_energy`
   - `sensor.gazpar2haws_total_cost` (if pricing configured)

### Test with Energy Dashboard

1. Go to **Energy** in the sidebar
2. Click **Add Consumption**
3. Select **Gas** tab
4. Choose `sensor.gazpar2haws_energy`
5. Save and wait for data to appear

## Troubleshooting

### Container Won't Start

**Check Docker is running:**
```bash
docker ps
```

**Rebuild the container:**
- `F1` → `Dev Containers: Rebuild Container`

**View Docker logs:**
```bash
docker logs <container-id>
```

### Home Assistant Not Accessible

**Check if supervisor_run is running:**
```bash
# In VS Code terminal
ps aux | grep supervisor
```

**Check ports are mapped correctly:**
```bash
docker ps
# Look for ports 7123:8123 and 7357:4357
```

**Try accessing different URL:**
- `http://localhost:7123/`
- `http://127.0.0.1:7123/`

**Check Home Assistant logs:**
```bash
ha core logs
```

### Add-on Not Appearing

**Check add-on directory structure:**
```bash
ls -la /mnt/supervisor/addons/local/
```

Your add-on should be at:
```
/mnt/supervisor/addons/local/gazpar2haws/
```

**Reload add-ons:**
```bash
ha addons reload
```

**Check supervisor logs:**
```bash
ha supervisor logs
```

### Permission Errors

The devcontainer runs in **privileged mode** for Docker-in-Docker support.

**If you still have permission issues:**
```bash
# Check user
whoami

# Check Docker socket
ls -la /var/run/docker.sock
```

### Slow Performance

**On Windows/Mac, improve performance:**
- Use WSL2 backend for Docker Desktop (Windows)
- Allocate more resources to Docker Desktop:
  - Settings → Resources → Advanced
  - Increase CPU and Memory

**Clean up Docker resources:**
```bash
docker system prune -a
```

### VS Code Extensions Not Loading

**Reload window:**
- `F1` → `Developer: Reload Window`

**Reinstall extensions:**
- `F1` → `Dev Containers: Rebuild Container`

## Cleanup

### Exit DevContainer

**Option A - Reopen Locally:**
- Click green button in bottom-left corner
- Select: `Reopen Folder Locally`

**Option B - Close VS Code:**
- Just close VS Code - container keeps running in background

### Stop the Container

```bash
# Find container ID
docker ps

# Stop container
docker stop <container-id>
```

### Remove Container and Volumes

**To completely clean up:**
```bash
# List containers
docker ps -a

# Remove container
docker rm <container-id>

# Remove volumes (WARNING: loses all data)
docker volume ls
docker volume rm <volume-name>
```

**Or rebuild from scratch:**
- `F1` → `Dev Containers: Rebuild Container`
- This keeps your settings but rebuilds the environment

## Development Workflow

### Typical Development Cycle

1. **Make code changes** in VS Code (files sync automatically)
2. **Restart the add-on** via UI or `ha addon restart gazpar2haws`
3. **Check logs** via UI or `ha addon logs gazpar2haws`
4. **Verify entities** in Settings → Entities
5. **Test functionality** in Home Assistant
6. **Repeat** until satisfied

### Running Tests

```bash
# Install dependencies (if needed)
poetry install

# Run unit tests
poetry run pytest tests/

# Run specific test
poetry run pytest tests/test_pricer.py -v

# Run linters
poetry run pylint gazpar2haws
poetry run black gazpar2haws
```

### Debugging

**Enable debug logging in add-on configuration:**
```yaml
logging:
  level: debug
```

**View detailed logs:**
```bash
ha addon logs gazpar2haws --follow
```

## Additional Resources

- **Home Assistant Developer Docs**: https://developers.home-assistant.io/docs/apps/testing/
- **DevContainer Docs**: https://code.visualstudio.com/docs/devcontainers/containers
- **Project Developer Guide**: See `/docs/DEVELOPER_GUIDE.md`
- **Main README**: See `/README.md`

## Quick Reference Commands

```bash
# Home Assistant
supervisor_run              # Start Home Assistant
ha core restart            # Restart Home Assistant Core
ha core logs               # View Home Assistant logs

# Add-ons
ha addon list              # List all add-ons
ha addon info gazpar2haws  # Show add-on info
ha addon start gazpar2haws # Start add-on
ha addon stop gazpar2haws  # Stop add-on
ha addon restart gazpar2haws # Restart add-on
ha addon logs gazpar2haws  # View add-on logs

# Supervisor
ha supervisor info         # Supervisor information
ha supervisor logs         # Supervisor logs

# Docker
docker ps                  # List running containers
docker logs <id>           # View container logs
```

## Support

If you encounter issues:

1. Check this README's [Troubleshooting](#troubleshooting) section
2. Review `/docs/DEVELOPER_GUIDE.md`
3. Check project [FAQ.md](/docs/FAQ.md)
4. Open an issue: https://github.com/ssenart/gazpar2haws/issues

---

**Happy developing!** 🚀
