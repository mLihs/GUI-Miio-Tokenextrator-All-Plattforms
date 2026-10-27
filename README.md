# Xiaomi Cloud Token Extractor

A powerful cross-platform desktop GUI application for extracting Xiaomi Cloud device tokens without command-line complexity. Built with Python and Qt for maximum compatibility.

![macOS](https://img.shields.io/badge/macOS-Apple%20Silicon%20%7C%20Intel-000000?style=flat&logo=apple)
![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D6?style=flat&logo=windows)
![Linux](https://img.shields.io/badge/Linux-Ubuntu%20%7C%20Debian-E95420?style=flat&logo=linux)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### Authentication
- 🔐 **Password Login** with 2FA email verification support
- 📱 **QR Code Login** - scan with your Xiaomi Home app
- 🤖 **CAPTCHA Handling** - automatic image display and verification
- 🔄 **Network Retry** - automatic retry with exponential backoff (3 attempts)
- ⚡ **Smart Error Messages** - user-friendly errors with actionable suggestions

### Device Management
- 🌍 **Multi-Region Support** - 8 server regions (CN, DE, US, RU, TW, SG, IN, I2)
- 🔍 **Real-time Search** - filter devices by name, IP, token, MAC, or model
- 📊 **Sortable Columns** - click any header to sort devices
- 🔑 **BLE Encryption Keys** - automatic retrieval for Bluetooth devices
- 🏠 **Hierarchical View** - organized by Server → Home → Device

### Copy & Export
- 📋 **Smart Copy/Paste**:
  - Right-click context menu for individual fields
  - Copy entire rows or multiple devices
  - Keyboard shortcut support (⌘+C / Ctrl+C)
  - Tab-separated format for spreadsheets
  
- 💾 **Multiple Export Formats**:
  - **CSV** - perfect for Excel/Google Sheets
  - **JSON** - structured data with full details
  - **YAML** - human-readable configuration format

### User Experience
- 💫 **Progress Indicators** - visual feedback during operations
- 💾 **Settings Persistence** - remembers window size, server selection, preferences
- 🎨 **Auto-resize Columns** - optimal readability
- 📝 **Integrated Log Viewer** - track operations and debug issues
- 🛡️ **Graceful Shutdown** - saves state and cancels operations cleanly

## 🚀 Quick Start

### Download & Run (Easiest)

**macOS:**
1. Download `XiaomiTokenExtractor-macOS.zip` from releases
2. Extract and right-click the app → **"Open"** (first time only - bypasses Gatekeeper)
3. Start extracting tokens!

**Windows:**
1. Download `XiaomiTokenExtractor-Windows.zip` from releases
2. Extract the folder anywhere
3. Run `XiaomiTokenExtractor.exe`

**Linux:**
1. Download `XiaomiTokenExtractor-Linux.tar.gz` from releases
2. Extract: `tar -xzf XiaomiTokenExtractor-Linux.tar.gz`
3. Make executable: `chmod +x XiaomiTokenExtractor`
4. Run: `./XiaomiTokenExtractor`

### Run from Source (All Platforms)

```bash
# Clone repository
git clone <repository-url>
cd Mac-Silicon-Miio-Tokenextrator

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate      # macOS/Linux
# or
.venv\Scripts\activate         # Windows

# Install dependencies
pip install .

# Run application
python -m token_extractor_gui
```

## 💻 Platform Support

| Platform | Status | Architecture | Download Format | Notes |
|----------|--------|--------------|-----------------|-------|
| **macOS** | ✅ Tested | Apple Silicon + Intel | `.zip` (contains `.app`) | M1/M2/M3 + Intel Macs |
| **Windows** | ✅ Tested | x64 | `.zip` (contains `.exe` + files) | Windows 10/11 |
| **Linux** | ✅ Tested | x64 | `.tar.gz` (single binary) | Ubuntu 20.04+ / Debian 11+ |

**Legend:**
- ✅ **Tested** - Verified working on actual hardware
- ⚠️ **CI Built** - Auto-built by GitHub Actions, community testing welcome

### Platform-Specific Notes

#### macOS
- **First launch**: Right-click → "Open" (bypasses Gatekeeper warning)
- **Quarantine removal**: `xattr -cr /path/to/XiaomiTokenExtractor.app`
- **Tested on**: macOS 15.1 (Sequoia) with Apple Silicon
- **Works on**: macOS 11.0+ (Big Sur and later)

#### Windows
- **Antivirus warnings**: May flag as unknown app - add exception if needed
- **No installation**: Just extract and run the .exe
- **Dependencies**: All bundled, no extra software needed
- **Compatibility**: Windows 10 (1809+) and Windows 11

#### Linux
- **System dependencies** (install if needed):
  ```bash
  sudo apt-get install libxcb-xinerama0 libxcb-cursor0
  ```
- **Tested distros**: Ubuntu 20.04+, Debian 11+ (should work on others)
- **Wayland**: Works, but X11 recommended for best compatibility

### Building from Source (Platform-Specific)

**macOS:**
```bash
pip install pyinstaller
pyinstaller XiaomiTokenExtractor.spec
open dist/XiaomiTokenExtractor.app
```

**Windows:**
```bash
pip install pyinstaller
pyinstaller XiaomiTokenExtractor-Windows.spec
dist\XiaomiTokenExtractor\XiaomiTokenExtractor.exe
```

**Linux:**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed \
  --name "XiaomiTokenExtractor" \
  --icon Xiaomi-cloud-tokens-extractor/icon.ico \
  --add-data "src/token_extractor_gui/assets/chevron-down.svg:assets" \
  src/token_extractor_gui/app.py
./dist/XiaomiTokenExtractor
```

## 🤖 Automated Builds (GitHub Actions)

This project uses **GitHub Actions** to automatically build for all platforms:
- **Triggers**: Git tags (`v*`), main branch commits, pull requests, manual dispatch
- **Platforms**: macOS (Apple Silicon), Windows (x64), Linux (x64)
- **Artifacts**: Available for 30 days after each build
- **Releases**: Auto-created for version tags with downloadable binaries

### Creating a Release

```bash
# Tag a new version
git tag -a v2.0.0 -m "Release v2.0.0: Cross-platform support"
git push origin v2.0.0

# GitHub Actions will automatically:
# 1. Build for macOS, Windows, Linux
# 2. Create GitHub Release
# 3. Attach all platform binaries
```

### Download CI Builds

1. Go to **Actions** tab in GitHub
2. Click on latest workflow run
3. Scroll to **Artifacts** section
4. Download for your platform

## 📖 How to Use

### 1. **Authentication**
Choose a method in the sidebar:
- **Password**: Enter Xiaomi account credentials
- **QR code**: Scan the code that appears with the Xiaomi Home app

### 2. **Select Server Region**
- Choose your region (or "All regions" to search everywhere)
- Most devices are in: CN (China), DE (Germany), US (United States)

### 3. **Fetch Devices**
- Click "Fetch devices" or "Sign in with QR"
- Wait for the progress bar to complete
- Devices appear organized by server and home

### 4. **Find & Copy Tokens**
- **Search**: Type in the search bar to filter devices
- **Copy**: Select a device and use the copy buttons, or right-click a row
- **Export**: Use the JSON, YAML, and CSV buttons in the status bar

## 🔧 Advanced Features

### Search & Filter
```
Type in search bar:
- Device name: "vacuum"
- IP address: "192.168"
- Token: "abc123"
- Model: "roborock"
```

### Copy Options
- **Individual field**: Right-click → Copy Token/IP/MAC/etc.
- **Entire row**: Right-click → Copy Row
- **Multiple devices**: Select with ⌘+Click, press ⌘+C
- **All devices**: Select multiple → Copy All Selected Devices

### Export Formats

**CSV** - Tab-separated values
```csv
Server,Home ID,Device Name,Device ID,Token,IP,MAC,Model,BLE Key
DE,123456,Living Room Vacuum,device_id,token123,192.168.1.10,...
```

**JSON** - Full structured data
```json
{
  "server": "de",
  "homes": [
    {
      "home_id": 123456,
      "devices": [...]
    }
  ]
}
```

**YAML** - Human-readable format
```yaml
server: de
homes:
  - home_id: 123456
    devices:
      - name: Living Room Vacuum
        token: abc123...
```

## 🛡️ Robustness & Stability

- **Network Retry Logic**: Automatic retry on connection failures (3 attempts)
- **User-Friendly Errors**: Clear error messages with troubleshooting steps
- **Graceful Shutdown**: Properly cancels operations and saves state
- **Settings Persistence**: All preferences saved between sessions
- **Thread Safety**: Proper cleanup and resource management

## 🔒 Security & Privacy

- ✅ Credentials sent **only** to official Xiaomi servers
- ✅ No third-party data collection
- ✅ Local storage only (no cloud sync)
- ✅ Open source - verify the code yourself

**Recommendations:**
- Use a dedicated Xiaomi account if concerned
- Enable 2FA on your Xiaomi account
- Keep tokens secure - they provide device access

## 📝 Requirements

### Pre-built Binaries
- **macOS**: 11.0+ (Big Sur or later), Apple Silicon or Intel
- **Windows**: 10 (1809+) or 11, 64-bit
- **Linux**: Ubuntu 20.04+ / Debian 11+ or equivalent, 64-bit
- **Network**: Active internet connection

### Building from Source
- **Python**: 3.10 or later
- **pip**: Latest version recommended
- **Platform**: Any OS that supports Python and Qt (macOS, Windows, Linux, *BSD)

## 🐛 Troubleshooting

### Platform-Specific Issues

#### macOS: App won't open (prohibition icon ⃠)
```bash
# Option 1: Remove quarantine flag
xattr -cr /path/to/XiaomiTokenExtractor.app

# Option 2: Right-click → Open (first time only)
```

#### Windows: "Windows protected your PC" warning
1. Click **"More info"**
2. Click **"Run anyway"**
3. Or add exception in Windows Defender

#### Windows: Antivirus flags the app
- **Why**: Unsigned executable from PyInstaller
- **Solution**: Add exception for `XiaomiTokenExtractor.exe`
- **Safe?**: Yes, verify source code or build yourself

#### Linux: Missing libraries error
```bash
# Install required libraries
sudo apt-get update
sudo apt-get install libxcb-xinerama0 libxcb-cursor0

# For other distros, install equivalent Qt/xcb packages
```

#### Linux: App won't start on Wayland
```bash
# Force X11 mode
QT_QPA_PLATFORM=xcb ./XiaomiTokenExtractor
```

### General Issues

#### Connection fails
- ✅ Check internet connection
- ✅ Try different server region
- ✅ Disable VPN temporarily
- ✅ Check firewall settings
- ✅ Ensure port 443 (HTTPS) is not blocked

#### Authentication fails
- ✅ Verify credentials (Xiaomi account, not Roborock!)
- ✅ Use QR code login instead
- ✅ Check spam folder for 2FA emails
- ✅ Wait if hitting rate limits (3-5 requests/day)
- ✅ Try browser login first to verify account works

#### No devices found
- ✅ Try "All regions" instead of specific server
- ✅ Verify devices appear in Xiaomi Home app
- ✅ Enable BLE checkbox for Bluetooth devices
- ✅ Wait 30-60 seconds for all regions to load

#### App crashes or freezes
- ✅ Check log viewer for error messages
- ✅ Try restarting the app
- ✅ Update to latest version
- ✅ Report issue with log output on GitHub

## 🏗️ Built With

- **[PySide6](https://wiki.qt.io/Qt_for_Python)** - Qt bindings for Python
- **[PyInstaller](https://pyinstaller.org/)** - Package to standalone app
- **[Requests](https://requests.readthedocs.io/)** - HTTP library
- **[PyCryptodome](https://pycryptodome.readthedocs.io/)** - Encryption (RC4)

## 👏 Credits

Built on top of [Piotr Machowski's Xiaomi Cloud Tokens Extractor](https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor). The core authentication and API logic comes from this excellent project.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

Includes and adapts code from Piotr Machowski's Xiaomi Cloud Tokens Extractor (MIT).

## ⚠️ Disclaimers

**General Use**
This software is provided "as is" without warranties. The authors are not liable for any damages or issues arising from use.

**Personal Use Only**
You are responsible for complying with Xiaomi's terms of service and local laws. Use at your own risk.

**Hardware / Firmware Notice**
This project interacts with physical devices and network services. Incorrect usage may lead to device malfunction, connection issues, or data loss.

**Reverse Engineering Notice**
Uses reverse-engineered protocols (miIO). Behavior may change due to vendor updates.

**Brand Independence**
Not affiliated with or endorsed by Xiaomi, SmartMi, Aqara, or any mentioned brands. All trademarks belong to their respective owners.

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## 📮 Support

- 🐛 **Bug Reports**: [GitHub Issues](../../issues)
- 💡 **Feature Requests**: [GitHub Discussions](../../discussions)
- 📖 **Documentation**: This README and inline code comments

---

**Made with ❤️ for the smart home community**
