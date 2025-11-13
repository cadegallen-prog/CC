# VSCode Setup Guide for Beginners in WSL Ubuntu

Welcome! You just set up WSL Ubuntu and VSCode. This guide will help you get your workspace configured perfectly for Python development.

---

## What I Just Set Up For You

### 1. Workspace Settings (`.vscode/settings.json`)

I configured your VSCode with beginner-friendly settings:

**Auto-formatting:**
- Your code will automatically format (look pretty) when you save
- Uses "Black" formatter (Python standard)

**Visual Helpers:**
- Line numbers shown
- Bracket colors (easier to see matching brackets)
- Error highlighting (shows errors inline with red text)
- Hidden clutter files (`__pycache__`, `.pyc` files)

**Python Setup:**
- Automatic import suggestions
- Type checking to catch errors
- Auto-activates your `venv` in terminals

**Git Integration:**
- Auto-fetch updates
- Smart commits enabled

### 2. Recommended Extensions (`.vscode/extensions.json`)

VSCode should show a popup asking if you want to install recommended extensions. Click "Install All"!

---

## Extensions Explained (What They Do)

### Essential Python Extensions
| Extension | What It Does | Why You Need It |
|-----------|--------------|-----------------|
| **Python** | Core Python support | Required for Python coding |
| **Pylance** | Smart code completion | Shows suggestions as you type |
| **Python Debugger** | Debug your code | Find and fix bugs visually |

### Jupyter (For Visual Coding)
| Extension | What It Does |
|-----------|--------------|
| **Jupyter** | Run notebooks in VSCode | Interactive coding, perfect for learning |
| **Jupyter Keymap** | Keyboard shortcuts | Faster navigation |
| **Jupyter Renderers** | Rich outputs | Beautiful charts and tables |

### Code Quality (Make Code Pretty)
| Extension | What It Does |
|-----------|--------------|
| **Black Formatter** | Auto-formats Python code | Makes code clean and readable |
| **Ruff** | Fast linter | Finds errors and suggests fixes |

### Helpful Tools
| Extension | What It Does | Beginner Benefit |
|-----------|--------------|------------------|
| **GitLens** | Visual Git tools | See who changed what, when |
| **Error Lens** | Inline error display | See errors right where they happen |
| **Spell Checker** | Checks spelling | Catches typos in comments |
| **Material Icon Theme** | Pretty file icons | Easier to identify file types |
| **Indent Rainbow** | Colors indentation | Easier to see code structure |
| **Rainbow CSV** | Colors CSV columns | Easier to read data files |
| **JSON** | Better JSON viewing | Easier to work with your data |

---

## How to Install Extensions

### Method 1: Automatic (Easiest)
1. VSCode should show a notification: "This workspace has extension recommendations"
2. Click **"Install All"**
3. Wait for them to install (takes 1-2 minutes)

### Method 2: Manual
1. Click the Extensions icon in the left sidebar (4 squares icon)
2. Search for the extension name
3. Click "Install"

### Method 3: Command Line
```bash
# Install all at once (copy this whole block)
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.debugpy
code --install-extension ms-toolsai.jupyter
code --install-extension ms-python.black-formatter
code --install-extension charliermarsh.ruff
code --install-extension eamodio.gitlens
code --install-extension streetsidesoftware.code-spell-checker
code --install-extension usernamehw.errorlens
code --install-extension PKief.material-icon-theme
code --install-extension oderwat.indent-rainbow
code --install-extension mechatroner.rainbow-csv
code --install-extension ZainChen.json
```

---

## What Each Setting Does

Open [.vscode/settings.json](.vscode/settings.json) to see all settings. Here are the important ones:

### Auto-Formatting
```json
"editor.formatOnSave": true
```
Every time you press Ctrl+S (save), your code gets cleaned up automatically.

### Python Environment
```json
"python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python"
```
Tells VSCode to use your virtual environment.

### Error Highlighting
```json
"errorLens.enabled": true
```
Shows errors right next to the problematic line (can't miss them!).

### Hidden Files
```json
"files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
}
```
Hides messy Python cache files from your file explorer.

---

## After Installing Extensions

### 1. Reload VSCode
Press `Ctrl+Shift+P` → type "Reload Window" → press Enter

### 2. Verify Python Setup
1. Open a new terminal (Ctrl+`)
2. You should see `(venv)` at the start of the prompt
3. Type: `python --version`
4. Should show: `Python 3.12.3`

### 3. Test Jupyter
1. Press `Ctrl+Shift+P`
2. Type "Jupyter: Create New Blank Notebook"
3. If it opens, you're good!

---

## Keyboard Shortcuts (Beginner Essentials)

| Shortcut | Action | Use It To... |
|----------|--------|--------------|
| `Ctrl+` ` | Open/close terminal | Run commands |
| `Ctrl+P` | Quick file open | Jump to any file |
| `Ctrl+Shift+P` | Command palette | Access all VSCode features |
| `Ctrl+S` | Save | Save (and auto-format) |
| `Ctrl+/` | Comment line | Add/remove comments |
| `Ctrl+Space` | Suggestions | See code completion options |
| `F5` | Start debugging | Run code with debugger |
| `Ctrl+B` | Toggle sidebar | More screen space |

---

## Troubleshooting

### Extensions Won't Install
1. Check internet connection
2. Try: `Ctrl+Shift+P` → "Extensions: Reload"
3. Restart VSCode

### Terminal Doesn't Show (venv)
1. Close all terminals
2. Open a new one
3. Should activate automatically now

### Python Not Found
1. `Ctrl+Shift+P` → "Python: Select Interpreter"
2. Choose: `./venv/bin/python`

### Formatter Not Working
1. Install Black formatter extension
2. `Ctrl+Shift+P` → "Format Document"
3. Select "Black" if prompted

---

## What's Different in WSL vs Windows?

| Aspect | Windows VSCode | WSL VSCode |
|--------|----------------|------------|
| **File Paths** | `C:\Users\...` | `/home/username/...` |
| **Terminal** | PowerShell/CMD | Bash (Linux shell) |
| **Commands** | Windows commands | Linux commands |
| **Performance** | Native | Slightly slower (but fine) |
| **Extensions** | Install in Windows | Install in WSL too |

**Important:** Some extensions need to be installed separately in WSL! If you see "Install in WSL: Ubuntu", click it.

---

## Next Steps

1. **Install the recommended extensions** (click "Install All" when prompted)
2. **Reload VSCode** (`Ctrl+Shift+P` → "Reload Window")
3. **Open a terminal** and verify `(venv)` appears
4. **Create a test file:**
   - Create `test.py`
   - Type: `print("Hello from WSL!")`
   - Save (Ctrl+S) - notice auto-formatting
   - Run: `python test.py` in terminal
5. **Try Jupyter:**
   - `Ctrl+Shift+P` → "Create New Blank Notebook"
   - Add a cell: `print("Jupyter works!")`
   - Click the play button

---

## Still Feeling Overwhelmed?

That's totally normal! Here's what to focus on first:

1. **Install the extensions** (just click "Install All")
2. **Open terminal, verify (venv) shows**
3. **Create and run a simple Python file**
4. **Ignore everything else for now**

You can explore other features as you go. The important thing is: **Python works, extensions installed, terminal shows (venv)**.

---

## Quick Reference

**Workspace Location:** `/home/cadegallen/Projects/product_type_identifier_repo`

**Virtual Environment:** `venv/` folder

**Python Path:** `venv/bin/python`

**Settings File:** `.vscode/settings.json`

**Extensions File:** `.vscode/extensions.json`

---

## Resources

- [VSCode Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [WSL Setup Guide](https://code.visualstudio.com/docs/remote/wsl)
- [Jupyter Notebooks Basics](https://code.visualstudio.com/docs/datascience/jupyter-notebooks)

---

**Remember:** You don't need to understand everything right now. Just get the extensions installed and make sure your terminal shows `(venv)`. Everything else can wait!
