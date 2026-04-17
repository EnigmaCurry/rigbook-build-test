# Android (Termux)

Experimentally, Rigbook runs on Android phones via [Termux](https://termux.dev) using
the pre-built Linux ARM64 binary inside a Debian proot environment.
The web UI is usable on phone touch screens, or you can use the phone just as the server, and have other devices access it. Rigbook is primarily
designed for desktop browsers.

```bash
# Install Termux from F-Droid, then:
pkg install proot-distro
proot-distro install debian
proot-distro login debian

# Inside Debian:
apt update && apt install -y wget
wget https://github.com/EnigmaCurry/rigbook/releases/latest/download/rigbook-linux-arm64
chmod +x rigbook-linux-arm64
```

**Important:** Android suspends background apps aggressively. Before
starting rigbook, acquire a wake lock so Termux stays alive when you
switch to the browser:

```bash
# In the debian proot (proot-distro login debian)
termux-wake-lock
./rigbook-linux-arm64
```

While termux is still running in the background, open your Android web browser and go to `http://127.0.0.1:8073` to access mobile Rigbook:


<p align="center">
  <img src="https://github.com/user-attachments/assets/e74d8446-8cfb-400d-a761-ee841b5c30c3" alt="Rigbook running on Android Pixel phone via Termux in Chrome browser" width="400"><br>
  <em>Rigbook running on Android Pixel phone via Termux in Chrome browser</em>
</p>


You can also use your phone as just the server, and access Rigbook from 
another computer's browser on the same network.  This gives you the full
desktop experience while you keep Rigbook running in your pocket. 
Set `RIGBOOK_HOST=0.0.0.0` before starting rigbook to listen on all interfaces:

```bash
# Warning: this allows any device to access your phone on port 8073 :
export RIGBOOK_HOST=0.0.0.0
termux-wake-lock
./rigbook-linux-arm64
```

Then open `http://<phone-ip>:8073` from any browser on the LAN.

**Warning:** Rigbook has no authentication or encryption — only do
this on trusted networks.
