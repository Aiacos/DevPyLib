# Neovim + mayapy: Simple Setup Methods

**TL;DR**: Non serve copiare file nella config globale! Usa uno di questi metodi automatici.

---

## 🏆 Metodo 1: File `.nvim.lua` Locale (CONSIGLIATO)

**Il più semplice e meno invasivo!**

### Cosa fa
- Neovim carica automaticamente `.nvim.lua` quando apri file in questo progetto
- Zero modifiche alla tua config globale
- Funziona solo per questo progetto

### Setup (1 minuto)

**Passo 1**: Abilita `exrc` in Neovim (una sola volta)

**Per AstroNvim Template v5** (modifica `~/.config/nvim/lua/polish.lua`):

```lua
-- This will run last in the setup process.
vim.opt.exrc = true  -- Abilita .nvim.lua local configs
```

**IMPORTANTE**: Rimuovi la riga `if true then return end` all'inizio del file!

**Per Neovim standard** (aggiungi a `~/.config/nvim/init.lua`):

```lua
vim.opt.exrc = true  -- Abilita config locali
```

**🔒 Sicurezza**: Neovim 0.9.0+ ha protezione integrata! Ti chiederà automaticamente
se fidarti del file `.nvim.lua` prima di eseguirlo. La vecchia opzione `secure = true`
è deprecata e **non funziona** per repository git clonati (tutti i file sono tuoi).

**Passo 2**: File `.nvim.lua` è già nel progetto! ✅

```bash
ls -la .nvim.lua  # Già presente!
```

**Passo 3**: Apri un file Maya in Neovim

```bash
cd /path/to/DevPyLib
nvim mayaLib/rigLib/base/module.py

# Neovim chiederà: "Trust .nvim.lua?" → Premi 'y'
# Fatto! LSP userà mayapy automaticamente
```

### Verifica funziona

```vim
:LspInfo                  " Mostra LSP attivi
:lua print(vim.lsp.get_active_clients()[1].config.settings.python.pythonPath)
" Output: /usr/autodesk/maya2024/bin/mayapy ✅
```

### Pro/Contro

✅ **Pro**:
- Zero modifiche config globale
- Automatico per tutti i file del progetto
- Facile da versione in git
- Ogni progetto può avere setup diverso

❌ **Contro**:
- Serve abilitare `exrc` (una sola volta)
- Neovim chiede conferma al primo uso (sicurezza)

---

## 🔥 Metodo 2: pyrightconfig.json (GIÀ FATTO!)

**Ancora più semplice - usa solo il file che abbiamo già!**

### Cosa fa
- Basedpyright legge automaticamente `pyrightconfig.json`
- Non serve nulla in Neovim
- Funziona anche con VS Code, PyCharm, etc.

### Setup (0 minuti)

**Il file è già presente!** ✅

```bash
cat pyrightconfig.json
```

```json
{
  "pythonVersion": "3.10",
  "pythonPlatform": "Linux",
  "executionEnvironments": [
    {
      "root": "mayaLib",
      "extraPaths": [
        "/usr/autodesk/maya2024/lib/python3.10/site-packages"
      ]
    }
  ],
  "reportMissingImports": false
}
```

### Come funziona

1. Basedpyright si avvia in Neovim
2. Cerca `pyrightconfig.json` nella directory
3. Usa le impostazioni automaticamente
4. **Non vede errori di import Maya** ✅

### Nota importante

Questo metodo **non cambia** l'interprete Python di Neovim, ma:
- ✅ Elimina errori di import (`maya.cmds`, `pymel.core`)
- ✅ Type checking corretto
- ❌ Test continuano a usare system Python (usa Metodo 1 o 3 per i test)

### Pro/Contro

✅ **Pro**:
- Zero configurazione (già fatto!)
- Funziona con qualsiasi editor
- Standard (pyrightconfig è documentato)

❌ **Contro**:
- Path Maya hardcoded (va aggiornato se cambia versione)
- Solo per type checking (non per eseguire codice)

---

## 🌳 Metodo 3: direnv + .envrc (AUTOMATICO)

**Imposta variabili d'ambiente automaticamente quando entri nella directory**

### Cosa fa
- `cd /path/to/DevPyLib` → variabili impostate automaticamente
- Funziona per shell, Neovim, tutti i tool
- Environment isolato per progetto

### Setup (3 minuti)

**Passo 1**: Installa direnv

```bash
# Ubuntu/Debian
sudo apt install direnv

# Fedora
sudo dnf install direnv

# macOS
brew install direnv

# Arch
sudo pacman -S direnv
```

**Passo 2**: Aggiungi hook alla shell

```bash
# Per bash (~/.bashrc)
eval "$(direnv hook bash)"

# Per zsh (~/.zshrc)
eval "$(direnv hook zsh)"

# Ricarica shell
source ~/.bashrc  # o ~/.zshrc
```

**Passo 3**: File `.envrc` è già nel progetto! ✅

```bash
cd /path/to/DevPyLib
direnv allow  # Autorizza .envrc (una sola volta)
```

Output:
```
✓ DevPyLib environment activated
  Python: /usr/autodesk/maya2024/bin/mayapy
```

**Passo 4**: Neovim userà automaticamente le variabili

```bash
nvim mayaLib/rigLib/base/module.py
# LSP usa mayapy automaticamente! ✅
```

### Come funziona

1. Entri nella directory → direnv esegue `.envrc`
2. `.envrc` imposta `$MAYAPY`, `$PYTHONPATH`, etc.
3. Neovim (e tutti i tool) vedono le variabili
4. LSP usa automaticamente mayapy

### Pro/Contro

✅ **Pro**:
- Automatico al 100%
- Funziona per tutti i tool (pytest, ruff, mypy, etc.)
- Environment isolato per progetto
- Shell-integrated (vedi variabili con `env`)

❌ **Contro**:
- Serve installare direnv
- Richiede hook nella shell
- Path Maya hardcoded in `.envrc`

---

## ⚡ Metodo 4: pyrightconfig.json + Auto-update

**pyrightconfig.json con path auto-aggiornato**

### Setup

Crea uno script che aggiorna `pyrightconfig.json` automaticamente:

```bash
# scripts/update_pyrightconfig.sh
#!/bin/bash
MAYAPY=$(python3 scripts/detect_mayapy.py)
SITE_PACKAGES=$(python3 scripts/detect_mayapy.py --site-packages)

# Aggiorna pyrightconfig.json
python3 -c "
import json
with open('pyrightconfig.json', 'r') as f:
    config = json.load(f)
config['executionEnvironments'][0]['extraPaths'] = ['$SITE_PACKAGES']
with open('pyrightconfig.json', 'w') as f:
    json.dump(config, f, indent=2)
"

echo "Updated pyrightconfig.json with: $MAYAPY"
```

Esegui una volta:
```bash
chmod +x scripts/update_pyrightconfig.sh
./scripts/update_pyrightconfig.sh
```

Aggiungi a pre-commit hook (opzionale):
```bash
# .git/hooks/post-checkout
#!/bin/bash
./scripts/update_pyrightconfig.sh
```

---

## 🎯 Metodo 5: Plugin Neovim dedicato

**Crea un mini-plugin locale**

### Setup

**Passo 1**: Crea directory plugin

```bash
mkdir -p ~/.local/share/nvim/site/pack/local/start/devpylib
```

**Passo 2**: Copia `.nvim/lsp_config.lua` lì

```bash
cp .nvim/lsp_config.lua ~/.local/share/nvim/site/pack/local/start/devpylib/lua/
```

**Passo 3**: Crea `plugin/init.lua`

```lua
-- ~/.local/share/nvim/site/pack/local/start/devpylib/plugin/init.lua
vim.api.nvim_create_autocmd("FileType", {
    pattern = "python",
    callback = function()
        -- Rileva se siamo in DevPyLib
        local cwd = vim.fn.getcwd()
        if string.match(cwd, "DevPyLib") then
            require('lsp_config').setup()
        end
    end,
})
```

Riavvia Neovim → funziona automaticamente per DevPyLib!

---

## 📊 Confronto Metodi

| Metodo | Setup | Invasività | Auto | Test |
|--------|-------|------------|------|------|
| **1. .nvim.lua** | 1 min | Minima | ✅ | ✅ |
| **2. pyrightconfig.json** | 0 min | Zero | ✅ | ❌ |
| **3. direnv** | 3 min | Minima | ✅ | ✅ |
| **4. Auto-update** | 2 min | Minima | ⚠️ | ❌ |
| **5. Plugin** | 5 min | Media | ✅ | ✅ |

**Legenda**:
- **Setup**: Tempo per configurare
- **Invasività**: Modifiche alla config globale
- **Auto**: Si attiva automaticamente
- **Test**: Supporta esecuzione test con mayapy

---

## 🏅 Raccomandazione

**Per la maggior parte degli utenti**: **Metodo 1 (.nvim.lua)**

```bash
# 1. Aggiungi a config Neovim (una sola volta):
#    - AstroNvim: ~/.config/nvim/lua/polish.lua → vim.opt.exrc = true
#    - Neovim: ~/.config/nvim/init.lua → vim.opt.exrc = true

# 2. Apri file:
nvim mayaLib/rigLib/base/module.py

# 3. Neovim chiede: "Trust .nvim.lua?" → Premi 'y'

# Fatto! ✅
```

**Bonus**: Combina **Metodo 1 + Metodo 3** per avere:
- LSP automatico (`.nvim.lua`)
- Test automatici (`direnv` → `pytest` usa mayapy)
- Zero config globale

---

## ❓ FAQ

### "Non vedo nessun messaggio quando apro Neovim"

Normale! `.nvim.lua` si carica silenziosamente. Verifica con:
```vim
:LspInfo
:lua print(vim.g.python3_host_prog)
```

### "Dice 'mayapy not found'"

Maya non è installato o non è in path standard. Opzioni:
1. Installa Maya
2. Modifica `.nvim.lua` con path manuale:
   ```lua
   local mayapy = "/percorso/custom/mayapy"
   ```

### "Voglio usare metodi diversi per progetti diversi"

Perfetto! Ogni progetto può avere:
- Progetto A: `.nvim.lua` con Maya 2024
- Progetto B: `.nvim.lua` con Maya 2023
- Progetto C: `.nvim.lua` con Houdini Python

### "pyrightconfig.json basta per VS Code?"

Sì! VS Code legge `pyrightconfig.json` automaticamente. Zero setup.

### "Posso usare questi metodi insieme?"

Sì! Si complementano:
- `.nvim.lua` → LSP Neovim
- `.envrc` → Environment shell/test
- `pyrightconfig.json` → Fallback per editor diversi

---

## 🔧 Troubleshooting

### Neovim non carica .nvim.lua

```lua
-- Verifica exrc è abilitato
:lua print(vim.o.exrc)  -- Deve essere true

-- Abilita manualmente (temporaneo)
:set exrc

-- Verifica versione Neovim (serve 0.9.0+)
:version
```

### LSP usa ancora system Python

```vim
# Riavvia LSP
:LspRestart

# O ricarica file
:edit
```

### direnv non funziona

```bash
# Verifica hook è attivo
type direnv

# Deve mostrare: "direnv is a function"

# Riautorizza .envrc
direnv allow
```

---

## 🔒 Sicurezza exrc: Cosa è cambiato

### ⚠️ Vecchio approccio (Vim/Neovim <0.9) - NON PIÙ SICURO

```lua
vim.o.exrc = true
vim.o.secure = true  -- ❌ NON funziona per git repos!
```

**Problema**: L'opzione `secure` controlla solo se il file è "owned by you".
Quando cloni un repository git, **tutti i file sono tuoi**, quindi `secure`
non protegge da nulla! Un `.nvim.lua` malintenzionato si esegue comunque.

### ✅ Nuovo approccio (Neovim 0.9.0+) - SICURO

```lua
vim.o.exrc = true  -- Basta questo!
```

**Protezione automatica**:
- Neovim **chiede conferma** prima di eseguire `.nvim.lua` sconosciuti
- Usa SHA256 hash per tracciare modifiche al file
- Ri-chiede conferma se il file cambia
- Database trust persistente in `stdpath('state')/trust`
- Puoi vedere il contenuto del file prima di accettare

**Esempio workflow**:
```bash
cd DevPyLib
nvim mayaLib/rigLib/base/module.py

# Neovim mostra:
# ┌───────────────────────────────────────────┐
# │ Trust .nvim.lua?                          │
# │ /home/user/DevPyLib/.nvim.lua             │
# │                                           │
# │ [y]es [n]o [v]iew                         │
# └───────────────────────────────────────────┘

# Premi 'v' per vedere il contenuto
# Premi 'y' per fidarti
# Premi 'n' per rifiutare
```

### 📋 Riferimenti

- [Neovim Issue #20911](https://github.com/neovim/neovim/issues/20911) - More secure exrc handling
- [Neovim PR #20956](https://github.com/neovim/neovim/pull/20956) - Implementation of vim.secure.read()

---

## 📜 Note Storiche - Metodi Alternativi

### Metodo astrocore.lua (Alternativa a polish.lua)

Se preferisci configurare `exrc` tramite `astrocore.lua` invece di `polish.lua`:

**File**: `~/.config/nvim/lua/plugins/astrocore.lua`

1. Rimuovi la riga: `if true then return {} end`
2. Aggiungi `exrc = true` nella sezione `options.opt`:

```lua
return {
  "AstroNvim/astrocore",
  opts = {
    options = {
      opt = {
        relativenumber = true,
        number = true,
        exrc = true,  -- <-- AGGIUNGI QUESTA RIGA
      },
    },
  },
}
```

**Nota**: `polish.lua` è più semplice perché usa Lua puro (`vim.opt.exrc = true`),
mentre `astrocore.lua` richiede la sintassi di configurazione AstroNvim.

---

## 📚 Risorse

- **exrc documentation**: `:help exrc` in Neovim
- **vim.secure documentation**: `:help vim.secure` in Neovim 0.9+
- **direnv website**: https://direnv.net/
- **pyrightconfig schema**: https://github.com/microsoft/pyright/blob/main/docs/configuration.md
- **AstroNvim config**: https://docs.astronvim.com/configuration/manage_user_config/

---

**Consiglio finale**: Prova **Metodo 1** per 5 minuti. Se ti piace, sei a posto. Se no, prova **Metodo 3** con direnv! 🚀
