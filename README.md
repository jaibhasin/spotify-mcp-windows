# Spotify‑MCP (Windows Edition)  
A Windows‑friendly fork / helper guide for running the **spotify‑mcp** Model‑Context‑Protocol (MCP) server locally and controlling Spotify through Claude Desktop (or any MCP‑enabled client).

> **What’s different?**  
> * Added a Python entry‑point (`main()` in `spotify_mcp/__init__.py`) so `python -c …` works on Windows.  
> * Tested with Conda + `spotipy==2.24.0` + `mcp==1.3.0`.  
> * Detailed Windows instructions, including Claude config and Spotify OAuth setup.

---

## 1. Prerequisites

| Tool | Version tested |
|------|----------------|
| **Python** | 3.9 – 3.11 (Conda) |
| **Conda**  | Anaconda / Miniconda |
| **git**    | latest |
| **Claude Desktop** | ≥ May 2025 build |
| **Spotify Premium** | required for playback API |

---

## 2. Clone & create environment

```powershell
git clone https://github.com/YOUR_USER/spotify-mcp-windows.git
cd spotify-mcp-windows

# create a clean env (feel free to choose another name / python version)
conda create -n spotify-mcp python=3.10
conda activate spotify-mcp
```

Install deps:

```powershell
pip install -r requirements.txt
# or explicitly
pip install spotipy==2.24.0 mcp==1.3.0 python-dotenv
```

---

## 3. Spotify Developer credentials

1. Go to <https://developer.spotify.com/dashboard> → **Create an App**  
2. Add redirect URI **`http://127.0.0.1:8000/callback`** (must match exactly).  
3. Copy **Client ID** and **Client Secret**.

Create `.env` (same folder as `src/`):

```dotenv
SPOTIFY_CLIENT_ID=YOUR_CLIENT_ID
SPOTIFY_CLIENT_SECRET=YOUR_CLIENT_SECRET
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback
```

> **Never commit `.env`** – it’s in `.gitignore`.

---

## 4. Claude Desktop configuration (Windows)

Open:  
`%APPDATA%\Claude\claude_desktop_config.json`

Add (or merge) the **`mcpServers`** block – replace paths & keys with your own:

```jsonc
{
  "mcpServers": {
    "spotify": {
      "command": "C:/Users/<YOU>/.conda/envs/spotify-mcp/python.exe",
      "args": [
        "-c",
        "import sys; sys.path.insert(0, 'C:/Users/<YOU>/spotify-mcp-windows/src'); from spotify_mcp import main; main()"
      ],
      "cwd": "C:/Users/<YOU>/spotify-mcp-windows",
      "env": {
        "SPOTIFY_CLIENT_ID": "YOUR_CLIENT_ID",
        "SPOTIFY_CLIENT_SECRET": "YOUR_CLIENT_SECRET",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8000/callback"
      }
    }
  }
}
```

> - **`command`** points to the *Conda env* Python.  
> - **`args`** import `spotify_mcp.main()` manually.  
> - Environment variables are injected so `spotipy` can authenticate.

Restart Claude Desktop → **Settings ▸ Manage MCPs** → you should see **spotify** (green once running).

---

## 5. Authorize Spotify

In a Claude chat:

```
Check my Spotify authentication
```

Claude opens the OAuth consent page. Click **Agree**.  
If the browser shows “connection refused”, that’s normal—the MCP already captured the token.

Claude should reply *“Spotify authenticated successfully”*.

---

## 6. Try it out

```text
Play some lofi beats
What song is playing?
Add this track to my Focus playlist
```

---

## 7. Troubleshooting

| Issue | Fix |
|-------|-----|
| `No client_id` error | Ensure Claude env block **and** `.env` have matching IDs. |
| Browser redirects to `/8000/` but Claude hangs | Confirm redirect URI matches in Spotify Dashboard **and** config. |
| “Server disconnected” AppleScript MCP | Ignore – that’s Claude’s built‑in Mac handler, not this project. |
| Port already in use | Change redirect URI to another free port (e.g., `8088`) in **all three** places (dashboard, `.env`, Claude). |

---

## 8. Security note

* `.env` is in `.gitignore`; never push real keys.  
* If you accidentally commit a secret, regenerate it in the Spotify dashboard and rewrite Git history (`git filter-repo …`) as shown in the cleanup guide.

---

## 9. License / credits

Original project by **[@varunneal](https://github.com/varunneal/spotify-mcp)**.  
This fork adds Windows setup tweaks and docs; see `LICENSE` for original terms.

---

Happy hacking – enjoy voice‑controlling Spotify on Windows via Claude! 🎧
