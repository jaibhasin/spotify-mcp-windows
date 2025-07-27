# Spotify‑MCP (Windows Edition)

![Windows](https://img.shields.io/badge/platform-Windows-blue)

A Windows-friendly launcher for the **spotify-mcp** Model‑Context‑Protocol server. Use it to control Spotify via Claude Desktop or any MCP-enabled client.

## What's different?

- Python entry point `spotify_mcp.main()` so `python -c ...` works on Windows.
- Tested with Conda, `spotipy==2.24.0` and `mcp==1.3.0`.
- Detailed Windows instructions for Claude config and Spotify OAuth.

---

## Prerequisites
| Tool | Version tested |
|------|----------------|
| **Python** | 3.9–3.11 (Conda) |
| **Conda** | Anaconda / Miniconda |
| **git** | latest |
| **Claude Desktop** | ≥ May 2025 build |
| **Spotify Premium** | required for playback API |

---

## Clone & create environment
```bash
git clone https://github.com/YOUR_USER/spotify-mcp-windows.git
cd spotify-mcp-windows
conda create -n spotify-mcp python=3.10
conda activate spotify-mcp
pip install -r requirements.txt
```

---

## Spotify Developer credentials
1. Visit <https://developer.spotify.com/dashboard> and **Create an App**.
2. Add redirect URI **`http://127.0.0.1:8000/callback`**.
3. Grab your **Client ID** and **Client Secret**.

Create `.env` (in the project root):

```dotenv
SPOTIFY_CLIENT_ID=<YOUR_CLIENT_ID>
SPOTIFY_CLIENT_SECRET=<YOUR_CLIENT_SECRET>
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback
```

Never commit `.env`—it's in `.gitignore`.

---

## Claude Desktop configuration (Windows)

Open `%APPDATA%\Claude\claude_desktop_config.json` and add:

```json
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
        "SPOTIFY_CLIENT_ID": "<YOUR_CLIENT_ID>",
        "SPOTIFY_CLIENT_SECRET": "<YOUR_CLIENT_SECRET>",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8000/callback"
      }
    }
  }
}
```

- **`command`** points to the Conda Python.
- **`args`** import `spotify_mcp.main()` manually.
- Variables allow `spotipy` to authenticate.

Restart Claude Desktop, then **Settings ▸ Manage MCPs** should list **spotify** in green.

---

## Running

```bash
python -m spotify_mcp --help
```

If needed, call the callback URL directly:

```bash
curl "http://127.0.0.1:8000/callback?code=<SPOTIFY_CODE>"
```

---

## Authorize Spotify

In a Claude chat:

```
Check my Spotify authentication
```

Claude opens the OAuth consent page. Click **Agree**. If the browser shows “connection refused” it just means the MCP captured the token. Claude should reply “Spotify authenticated successfully.”

---

## Try it out

```text
Play some lofi beats
What song is playing?
Add this track to my Focus playlist
```

---

## Troubleshooting
| Issue | Fix |
|-------|-----|
| `No client_id` error | Check both Claude env block and `.env`. |
| Browser redirects to `/8000/` but Claude hangs | Ensure redirect URI matches everywhere. |
| “Server disconnected” AppleScript MCP | Ignore—Claude’s macOS handler. |
| Port already in use | Pick another port in all places (`8088` etc.). |

---

## Development

```bash
flake8 src       # lint
pytest           # run tests (currently minimal)
```

Contributions welcome—open issues or PRs.

---

## Security note
- `.env` is git‑ignored; never push real keys.
- If you leak a secret, regenerate it in the Spotify dashboard and rewrite history.

---

## License / credits

Based on [@varunneal/spotify-mcp](https://github.com/varunneal/spotify-mcp). See `LICENSE` for original terms.

Happy hacking – enjoy voice‑controlling Spotify on Windows via Claude! 🎧
