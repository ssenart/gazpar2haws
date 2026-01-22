# Testing Gazpar2HAWS Add-on in Home Assistant

This guide helps you test the add-on directly in Home Assistant to replicate issue #105 (segmentation fault).

## Prerequisites

- Home Assistant 2026.1.x running (to replicate the issue)
- Access to Home Assistant UI
- Access to add-on logs

## Method 1: Test with Local Add-on Repository (Recommended)

This method allows you to test your local development version without publishing.

### Step 1: Prepare Local Repository

1. **Find your repository URL**:
   - If using GitHub: `https://github.com/ssenart/gazpar2haws`
   - For local testing with your branch: `https://github.com/ssenart/gazpar2haws` and specify branch

### Step 2: Add Repository to Home Assistant

1. Open Home Assistant
2. Go to **Settings** → **Add-ons** → **Add-on Store**
3. Click the **⋮** (three dots) in the top right
4. Select **Repositories**
5. Add your repository URL: `https://github.com/ssenart/gazpar2haws`
6. Click **Add**

### Step 3: Install the Add-on (Current Alpine Version)

1. In the Add-on Store, find **Gazpar2HAWS**
2. Click on it
3. Click **Install**
4. Wait for installation to complete
5. **DO NOT START YET** - Configure it first

### Step 4: Configure the Add-on

1. Go to the **Configuration** tab
2. Fill in your GrDF credentials:
   ```yaml
   devices:
     - name: gazpar2haws
       username: "your-email@example.com"
       password: "your-password"
       pce_identifier: "your-pce-id"
       timezone: "Europe/Paris"
   ```
3. Click **Save**

### Step 5: Start and Monitor for Segfault

1. Go to the **Info** tab
2. Click **Start**
3. Immediately go to the **Log** tab
4. Watch for the segmentation fault:
   ```
   Segmentation fault (core dumped) python3 -m gazpar2haws
   ```
5. Check if the add-on status shows:
   - **Exit code 139** (indicates segfault)
   - Add-on keeps restarting and failing

### Step 6: Check System Logs

If the add-on log doesn't show details:

1. Go to **Settings** → **System** → **Logs**
2. Look for supervisor logs
3. Search for "gazpar2haws" entries with exit code 139

## Method 2: Test with Development Build

If you want to test your local changes before publishing:

### Option A: Build Locally with Docker

1. Navigate to the add-on directory:
   ```bash
   cd addons/gazpar2haws
   ```

2. Build the add-on manually:
   ```bash
   docker build --build-arg BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.20 --build-arg GAZPAR2HAWS_VERSION=0.5.0a2 -t local/gazpar2haws-test .
   ```

3. Run it standalone to test:
   ```bash
   docker run --rm local/gazpar2haws-test
   ```

### Option B: Use Local Add-on Development

1. **Enable Advanced Mode** in your Home Assistant profile

2. **Copy add-on to HA addons folder**:
   - If using HAOS: You'll need to use SSH or Samba to access `/addons/`
   - If using Docker: Mount your local addons folder
   - If using Supervised: Copy to `/usr/share/hassio/addons/local/`

3. **Create local repository**:
   ```bash
   # In your HA addons folder
   mkdir -p local/gazpar2haws
   cp -r /path/to/your/gazpar2haws/addons/gazpar2haws/* local/gazpar2haws/
   ```

4. **Reload add-ons**: Settings → Add-ons → ⋮ → Reload

5. **Install from Local**: The add-on should appear in your add-on store

## Expected Results

### Current Alpine Version (Should Fail)
- **Exit code**: 139
- **Log message**: "Segmentation fault (core dumped)"
- **Add-on status**: Failed/Crashed
- **Restart behavior**: Keeps restarting and failing

### After Debian Fix (Should Work)
- **Exit code**: 0 or running
- **Log message**: Normal startup messages
- **Add-on status**: Running
- **Behavior**: Successfully connects and imports data

## Troubleshooting

### Add-on not appearing in store
- Check that repository.yaml exists in your repo
- Verify the repository URL is correct
- Try removing and re-adding the repository

### Cannot access logs
- Logs are in: Settings → Add-ons → Gazpar2HAWS → Log tab
- Or use: `ha addons logs local_gazpar2haws`

### Want to test specific branch
- When adding repository, some HA versions allow specifying branch
- Or fork the repo and test from your fork

## Testing the Fix

After implementing the Debian-based fix:

1. Update `build.yaml` with Debian images
2. Commit and push to your test branch
3. In HA, update the add-on or reinstall
4. Start the add-on
5. Verify it runs without segfault
6. Check logs show successful startup

## Home Assistant Version Requirements

- **To replicate issue**: Use Home Assistant 2026.1.x
- **Previous versions**: Issue might not occur on HA 2025.x with Python 3.12
