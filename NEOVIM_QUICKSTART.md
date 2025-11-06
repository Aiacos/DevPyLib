# Neovim + Maya: 1-Minute Setup

**Problema**: Neovim mostra errori per `import maya.cmds`, `import pymel.core`

**Soluzione**: Usa mayapy come interprete Python → **0 errori** ✅

---

## 🚀 Quick Start (Metodo Più Semplice)

### Opzione A: File Locale `.nvim.lua` (1 minuto)

**Step 1**: Abilita config locali in Neovim (una sola volta)

**AstroNvim** (modifica `~/.config/nvim/lua/polish.lua`):
```lua
vim.opt.exrc = true  -- Abilita .nvim.lua local configs
```
*Rimuovi la riga: `if true then return end`*

**Neovim standard** (aggiungi a `~/.config/nvim/init.lua`):
```lua
vim.opt.exrc = true
```

**Step 2**: Apri un file Python in questo progetto

```bash
cd /path/to/DevPyLib
nvim mayaLib/rigLib/base/module.py
```

**Step 3**: Conferma il file locale quando Neovim chiede

```
Trust .nvim.lua? (y/n): y
```

**Fatto!** LSP ora usa mayapy automaticamente ✅

---

### Opzione B: pyrightconfig.json (0 minuti - già configurato!)

**Nessun setup necessario!** Il file `pyrightconfig.json` è già nel progetto.

Basedpyright lo legge automaticamente e:
- ✅ Non mostra errori per import Maya
- ✅ Type checking corretto
- ✅ Funziona anche in VS Code, PyCharm, etc.

**Nota**: Aggiorna i path se usi una versione Maya diversa da 2024:

```bash
./scripts/update_pyrightconfig.sh
```

---

### Opzione C: direnv (automatico per shell + Neovim)

**Step 1**: Installa direnv

```bash
# Ubuntu/Debian
sudo apt install direnv

# Fedora
sudo dnf install direnv

# macOS
brew install direnv
```

**Step 2**: Aggiungi hook

```bash
# ~/.bashrc o ~/.zshrc
eval "$(direnv hook bash)"  # o zsh
```

**Step 3**: Autorizza directory

```bash
cd /path/to/DevPyLib
direnv allow
```

Output:
```
✓ DevPyLib environment activated
  Python: /usr/autodesk/maya2024/bin/mayapy
```

**Fatto!** Environment attivo per shell, Neovim, pytest ✅

---

## ✅ Verifica Funziona

```vim
:LspInfo
" Mostra: basedpyright attached

:lua print(vim.lsp.get_active_clients()[1].config.settings.python.pythonPath)
" Output: /usr/autodesk/maya2024/bin/mayapy
```

Apri un file con import Maya:
```python
import pymel.core as pm  # ✅ No error!
pm.ls()  # ✅ Autocomplete works!
```

---

## 🧪 Test con mayapy

```bash
# Esegui test con mayapy
./scripts/test_with_maya.sh

# Con opzioni pytest
./scripts/test_with_maya.sh -v -k test_control

# Solo unit test
./scripts/test_with_maya.sh -m unit
```

---

## 📚 Documentazione Completa

- **Setup semplificato**: [NEOVIM_SIMPLE_SETUP.md](NEOVIM_SIMPLE_SETUP.md)
- **Setup dettagliato**: [NEOVIM_MAYAPY_SETUP.md](NEOVIM_MAYAPY_SETUP.md)
- **Script utilities**: [scripts/README.md](scripts/README.md)

---

## 🔧 Troubleshooting

### "mayapy not found"

```bash
# Verifica Maya è installato
ls -la /usr/autodesk/maya*/bin/mayapy

# Manuale: modifica .nvim.lua
vim .nvim.lua
# Cambia: local mayapy = "/percorso/custom/mayapy"
```

### "Neovim non carica .nvim.lua"

```vim
" Verifica exrc è abilitato
:set exrc?
" Deve mostrare: exrc

" Se no, abilita:
:set exrc

" Verifica versione Neovim (serve 0.9.0+)
:version
```

**Nota sicurezza**: Neovim 0.9.0+ chiede automaticamente conferma prima
di eseguire `.nvim.lua`. NON usare `secure = true` (deprecato e non funziona
per repository git clonati).

### "LSP mostra ancora errori Maya"

```vim
" Riavvia LSP
:LspRestart

" O ricarica file
:edit
```

---

## 🏆 Confronto Metodi

| Metodo | Tempo | Invasività | Auto | Test |
|--------|-------|------------|------|------|
| **.nvim.lua** | 1 min | Minima | ✅ | ✅ |
| **pyrightconfig** | 0 min | Zero | ✅ | ❌ |
| **direnv** | 3 min | Minima | ✅ | ✅ |

**Consiglio**: Inizia con **.nvim.lua** (più veloce) o **pyrightconfig** (zero setup)

---

## ❓ FAQ

**Q**: Devo modificare la mia config Neovim globale?
**A**: No! `.nvim.lua` è locale al progetto.

**Q**: Funziona con VS Code?
**A**: Sì! `pyrightconfig.json` funziona automaticamente.

**Q**: Posso usare più metodi insieme?
**A**: Sì! Si complementano (LSP + tests).

**Q**: Cosa succede se cambio versione Maya?
**A**: Esegui `./scripts/update_pyrightconfig.sh` per aggiornare i path.

**Q**: Serve installare mayapy?
**A**: No, mayapy viene con Maya. Serve solo Maya installato.

---

**Preferisci video tutorial?** Apri issue su GitHub! 🎥
