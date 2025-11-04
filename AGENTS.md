# Repository Guidelines
DevPyLib streamlines Maya-first workflows with expanding Houdini, Blender, and Prism tooling. These guidelines capture how the repository fits together so contributors can deliver focused, production-ready changes quickly.

## Project Structure & Module Organization
- `mayaLib/` is the primary codebase: rigging (`rigLib/`), Bifrost (`bifrostLib/`), fluids (`fluidLib/`), GUI (`guiLib/`), shader, pipeline, and plugin modules.
- Tests and harnesses live in `mayaLib/test/`.
- `houdiniLib/`, `blenderLib/`, and `prismLib/` host DCC-specific adapters that mirror Maya patterns.
- `pyfrost/` is a submodule providing shared Bifrost utilities; update it whenever you touch graph tooling.
- `tools/` contains standalone scripts (texture utilities and converters) referenced from pipeline docs.

## Build, Test, and Development Commands
- `git submodule update --init --recursive` keeps `pyfrost/` in sync after clone or branch switches.
- `mayapy -m pip install -r requirements.txt` installs Python dependencies into the Maya interpreter; run again after dependency bumps.
- `ln -s $PWD/userSetup.py ~/maya/scripts/userSetup.py` (adjust per OS) enables auto-loading inside Maya; copy instead if symlinks are unavailable.
- `mayapy userSetup.py --` (no args) is a quick smoke-test: it should print the detected library path and import summary without errors.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation; keep lines ≤ 120 chars to respect Maya Script Editor limits.
- Use `camelCase` for Maya node names, `snake_case` for functions, and `PascalCase` for classes; match existing module patterns before introducing new namespaces.
- Import `pymel.core as pm` when interacting with Maya scenes; prefer utility wrappers in `mayaLib/utility/` over raw cmds.
- Every public function needs a docstring—UI generation relies on introspection to populate menus and tooltips.

## Testing Guidelines
- Execute regression suites inside Maya: `execfile('/path/to/DevPyLib/mayaLib/test/MayaLib.py')` from the Script Editor (Python tab).
- When adding tooling, provide a minimal scene or asset in `mayaLib/test/assets/` if manual validation is required.
- Record platform coverage in the PR description; target at least Windows plus one additional OS when features touch filesystem or UI code.

## Commit & Pull Request Guidelines
- Write imperative commits with optional scope prefixes, e.g. `Refactor: Streamline fluid solver caching` or `Fix rigLib: Preserve mirror weights`.
- Rebase before opening a PR, include a concise summary, testing notes, and link to any relevant issue or task tracker ticket.
- Attach screenshots or GIFs when changes affect UI output, and mention any new Maya environment variables or menu entries.

## Configuration Tips
- Keep `userSetup.py` lightweight: add feature toggles via environment variables or `mayaLib/pipelineLib/config/`.
- For custom ports or auto-update hooks, edit the constants in `userSetup.py` (documented near lines 90–110) rather than hard-coding values in new modules.
