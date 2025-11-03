# DevPyLib - Migrazione Cross-Platform

## Riepilogo Modifiche

DevPyLib è stato aggiornato per essere completamente compatibile con **Windows, Linux e macOS** senza richiedere configurazioni manuali o path hardcoded.

---

## 📋 Modifiche Implementate

### 1. **userSetup.py** - Auto-rilevamento Path
**Problema originale:**
- Path hardcoded a `~/Documents/workspace/DevPyLib`
- `os.system()` per pip install (non sicuro e non cross-platform)

**Soluzione implementata:**
- ✅ Auto-rilevamento della posizione usando `Path(__file__).parent`
- ✅ Uso di `subprocess` invece di `os.system()` per pip install
- ✅ GitPython reso opzionale (non blocca se non installato)
- ✅ Migliore gestione errori e logging
- ✅ Timeout di 5 minuti per pip install

**Come funziona ora:**
```python
# Il path viene rilevato automaticamente
libDir = Path(__file__).parent.resolve().as_posix()
print(f"DevPyLib detected at: {libDir}")
```

---

### 2. **libManager.py** - Fix Bug Cross-Platform
**Problemi originali:**
- Path OSX errato: `/Library/Preferences/Autodesk` (mancava `~/`)
- Bug Windows: usava `linuxPath` invece di `winPath`
- Workspace hardcoded a `Documents/workspace`
- Maya.env path hardcoded
- Comandi Unix (`rm`, `unzip`) non funzionanti su Windows

**Soluzioni implementate:**
- ✅ Rilevamento corretto dei path per ogni OS:
  - **Linux**: `~/maya/scripts` o `~/Documents/maya/scripts`
  - **macOS**: `~/Library/Preferences/Autodesk/maya/scripts`
  - **Windows**: `%USERPROFILE%\Documents\maya\scripts`
- ✅ Workspace path con fallback intelligente
- ✅ Maya.env path rilevato correttamente per ogni OS
- ✅ Uso di `shutil` e `zipfile` invece di comandi shell
- ✅ Tutte le operazioni file ora cross-platform

**Esempio rilevamento path:**
```python
if current_platform == "Linux":
    self.mayaScriptPath = self.homeUser / "maya" / "scripts"
    if not self.mayaScriptPath.exists():
        self.mayaScriptPath = self.homeUser / "Documents" / "maya" / "scripts"
elif current_platform == "Darwin":  # macOS
    self.mayaScriptPath = self.homeUser / "Library" / "Preferences" / "Autodesk" / "maya" / "scripts"
elif current_platform == "Windows":
    self.mayaScriptPath = self.homeUser / "Documents" / "maya" / "scripts"
```

---

### 3. **Converter Scripts** - Soluzioni Cross-Platform
**Problema originale:**
- `converter.bat` con path hardcoded Windows-only

**Soluzioni implementate:**
- ✅ **converter.py** - Script Python universale (tutti gli OS)
- ✅ **converter.sh** - Shell script per Linux/macOS (eseguibile)
- ✅ **converter.bat** - Aggiornato senza path hardcoded

**Uso:**
```bash
# Linux/macOS
./converter.sh
# oppure
python converter.py

# Windows
converter.bat
# oppure
python converter.py
```

---

## 🚀 Installazione Cross-Platform

### Metodo 1: Installazione Automatica (Consigliato)

1. **Clona il repository** dove preferisci:
   ```bash
   # Posizione suggerita ma non obbligatoria
   cd ~/Documents/workspace  # o ~/workspace su Linux
   git clone https://github.com/Aiacos/DevPyLib.git
   ```

2. **Copia/Linka userSetup.py** nella cartella scripts di Maya:

   **Linux:**
   ```bash
   # Crea un symlink (consigliato)
   ln -s ~/Documents/workspace/DevPyLib/userSetup.py ~/maya/scripts/userSetup.py

   # Oppure copia il file
   cp ~/Documents/workspace/DevPyLib/userSetup.py ~/maya/scripts/
   ```

   **macOS:**
   ```bash
   ln -s ~/Documents/workspace/DevPyLib/userSetup.py \
         ~/Library/Preferences/Autodesk/maya/scripts/userSetup.py
   ```

   **Windows (PowerShell da Amministratore):**
   ```powershell
   # Symlink (consigliato)
   New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\Documents\maya\scripts\userSetup.py" `
            -Target "$env:USERPROFILE\Documents\workspace\DevPyLib\userSetup.py"

   # Oppure copia manualmente il file
   ```

3. **Riavvia Maya** - DevPyLib verrà caricato automaticamente!

---

### Metodo 2: Posizione Personalizzata

Puoi clonare DevPyLib **ovunque** e creare il symlink da lì:

```bash
# Esempio: clonare in ~/projects
cd ~/projects
git clone https://github.com/Aiacos/DevPyLib.git

# Poi creare symlink
ln -s ~/projects/DevPyLib/userSetup.py ~/maya/scripts/userSetup.py
```

Il path verrà rilevato automaticamente! 🎉

---

## 📝 Maya.env (Opzionale)

**Maya.env NON è più necessario!** userSetup.py configura tutto automaticamente.

Se vuoi comunque usare Maya.env (per esempio per configurazioni aggiuntive), puoi usare `libManager.copyToMayaEnv()` che ora supporta tutti gli OS.

---

## 🔧 Dipendenze

Il file `requirements.txt` contiene:
```
numpy
pathlib
pymel
GitPython
```

Queste vengono installate automaticamente al primo avvio di Maya tramite userSetup.py.

---

## 🎯 Vantaggi della Nuova Implementazione

1. ✅ **Zero configurazione manuale** - funziona "out of the box"
2. ✅ **Posizione flessibile** - DevPyLib può stare ovunque
3. ✅ **Cross-platform nativo** - Windows, Linux, macOS
4. ✅ **Migliore gestione errori** - logging dettagliato
5. ✅ **Più sicuro** - usa subprocess invece di os.system
6. ✅ **GitPython opzionale** - non blocca se mancante
7. ✅ **Timeout pip install** - non si blocca indefinitamente

---

## 🧪 Testing

Per verificare che tutto funzioni:

1. **Avvia Maya**
2. **Apri Script Editor**
3. **Verifica l'output:**
   ```
   DevPyLib detected at: /path/to/DevPyLib
   All requirements installed successfully!
   Added /path/to/DevPyLib to sys.path
   Imported mayaLib
   Maya command port opened on: 4434
   DevPyLib setup complete!
   ```

4. **Verifica il menu** - Dovresti vedere il menu DevPyLib nella UI di Maya

---

## 🐛 Risoluzione Problemi

### Il menu non appare
- Verifica che il symlink/copia di userSetup.py sia corretto
- Controlla Script Editor per eventuali errori
- Verifica che mayaLib/__init__.py esista

### Errori di import
- Assicurati che tutte le dipendenze siano installate: `pip install -r requirements.txt`
- Verifica che il path sia corretto: controlla l'output "DevPyLib detected at:"

### Git pull non funziona
- GitPython è opzionale, il sistema funziona anche senza
- Per abilitare: installa GitPython e decommenta la riga in userSetup.py:
  ```python
  git_pull_gitpython(libDir, branch="master")
  ```

---

## 📚 Prossimi Passi

Ora che DevPyLib è cross-platform, puoi:

1. ✅ Sviluppare su qualsiasi OS
2. ✅ Condividere configurazioni nel team
3. ✅ Usare CI/CD multi-piattaforma
4. ✅ Testing automatico su Linux/macOS/Windows

---

## 🔍 File Modificati

```
✏️  userSetup.py              - Auto-rilevamento path + subprocess
✏️  mayaLib/pipelineLib/utility/libManager.py - Fix cross-platform completo
✏️  tools/converter.bat       - Rimosso path hardcoded
➕  tools/converter.py         - Nuovo script Python universale
➕  tools/converter.sh         - Nuovo script shell Linux/macOS
➕  CROSS_PLATFORM_MIGRATION.md - Questo documento
```

---

## 📧 Support

Per problemi o domande:
- GitHub Issues: https://github.com/Aiacos/DevPyLib/issues
- Controlla CLAUDE.md per architettura e best practices

---

**Buon lavoro con DevPyLib! 🎨🔥**
