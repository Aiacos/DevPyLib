-- ============================================================================
-- DevPyLib Local Neovim Configuration
--
-- This file configures LSP to use Maya's Python interpreter (mayapy) for
-- proper import resolution of maya.cmds, pymel.core, etc.
--
-- REQUIREMENTS:
--   - Neovim 0.9.0+ (has built-in secure .nvim.lua support)
--   - basedpyright LSP server
--   - exrc enabled in your config
--
-- OPTIONAL (for test execution):
--   - neotest + neotest-python (for running tests in Neovim)
--
-- SETUP FOR ASTRONVIM (Template v5):
--   Edit ~/.config/nvim/lua/polish.lua
--     1. Remove: if true then return end
--     2. Add: vim.opt.exrc = true
--
-- SETUP FOR NEOVIM STANDARD:
--   Add to ~/.config/nvim/init.lua:
--     vim.opt.exrc = true
--
-- SECURITY:
--   Neovim 0.9.0+ will prompt you to trust this file before executing it.
--   This uses Neovim's built-in vim.secure trust database (automatic).
--   The old 'secure' option is deprecated and doesn't protect against
--   cloned repositories (all files are owned by you).
--
-- This is the LEAST INVASIVE method - no global config changes needed!
-- ============================================================================

-- Detect mayapy path
local function detect_mayapy()
    -- Try detection script
    local handle = io.popen("python3 scripts/detect_mayapy.py 2>/dev/null")
    if handle then
        local result = handle:read("*a")
        handle:close()
        if result and result ~= "" then
            return result:gsub("\n", "")
        end
    end

    -- Fallback to common paths
    local paths = {
        "/usr/autodesk/maya2024/bin/mayapy",
        "/usr/autodesk/maya2025/bin/mayapy",
        "/usr/autodesk/maya2026/bin/mayapy",
    }
    for _, path in ipairs(paths) do
        if vim.fn.executable(path) == 1 then
            return path
        end
    end

    return nil
end

-- Get Maya site-packages
local function get_site_packages(mayapy)
    if not mayapy then
        return nil
    end

    local handle = io.popen(mayapy .. ' -c "import site; print(site.getsitepackages()[0])" 2>/dev/null')
    if handle then
        local result = handle:read("*a")
        handle:close()
        return result:gsub("\n", "")
    end
    return nil
end

-- Setup basedpyright with mayapy
local function setup_lsp()
    local mayapy = detect_mayapy()
    if not mayapy then
        vim.notify("[DevPyLib] mayapy not found, using system Python", vim.log.levels.WARN)
        return
    end

    local site_packages = get_site_packages(mayapy)

    -- Check if lspconfig is available
    local ok, lspconfig = pcall(require, "lspconfig")
    if not ok then
        return
    end

    -- Update basedpyright settings if it's running
    local clients = vim.lsp.get_active_clients({ bufnr = 0, name = "basedpyright" })
    if #clients > 0 then
        for _, client in ipairs(clients) do
            client.config.settings.python = { pythonPath = mayapy }
            if site_packages then
                client.config.settings.basedpyright.analysis.extraPaths = { site_packages }
            end
            client.notify("workspace/didChangeConfiguration", { settings = client.config.settings })
        end
        vim.notify("[DevPyLib] Updated LSP to use: " .. mayapy, vim.log.levels.INFO)
    else
        -- Configure for when LSP starts
        lspconfig.basedpyright.setup({
            settings = {
                basedpyright = {
                    analysis = {
                        extraPaths = site_packages and { site_packages } or {},
                    },
                },
                python = {
                    pythonPath = mayapy,
                },
            },
        })
    end
end

-- Setup neotest to use mayapy for running tests
local function setup_neotest()
    local mayapy = detect_mayapy()
    if not mayapy then
        return -- No mayapy found, skip neotest config
    end

    -- Check if neotest is installed
    local has_neotest, neotest = pcall(require, "neotest")
    if not has_neotest then
        return -- Neotest not installed
    end

    -- Check if neotest-python adapter is available
    local has_python_adapter, python_adapter = pcall(require, "neotest-python")
    if not has_python_adapter then
        return -- neotest-python adapter not installed
    end

    -- Configure neotest with mayapy
    local adapters = {
        python_adapter({
            -- Use mayapy instead of system python
            python = mayapy,
            -- Use pytest as test runner
            runner = "pytest",
            -- Pytest arguments
            args = { "-vv", "--tb=short", "--log-level=DEBUG" },
            -- DAP configuration for debugging
            dap = { justMyCode = false },
        }),
    }

    -- Setup neotest
    neotest.setup({
        adapters = adapters,
        discovery = {
            enabled = true,
        },
        running = {
            concurrent = false, -- Maya doesn't support parallel execution
        },
        diagnostic = {
            enabled = true,
        },
    })

    vim.notify("[DevPyLib] Neotest configured to use: " .. mayapy, vim.log.levels.INFO)
end

-- Run setup
setup_lsp()
setup_neotest()

-- Optional: Set local python3 provider (for Neovim's :py3 commands)
local mayapy = detect_mayapy()
if mayapy then
    vim.g.python3_host_prog = mayapy
end
