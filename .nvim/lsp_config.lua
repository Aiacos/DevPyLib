-- ============================================================================
-- DevPyLib Neovim LSP Configuration
--
-- This module configures Language Server Protocol (LSP) for DevPyLib to use
-- Maya's Python interpreter (mayapy) instead of system Python.
--
-- Features:
-- - Auto-detects mayapy installation
-- - Configures basedpyright with Maya paths
-- - Sets up ruff_lsp for linting
-- - Provides sensible keybindings
-- - Handles Maya/PyMEL imports correctly
--
-- Usage:
--   1. Copy this file to your Neovim config:
--      ~/.config/nvim/lua/devpylib_lsp.lua
--
--   2. Source it in your init.lua:
--      require('devpylib_lsp').setup()
--
--   3. Or copy relevant parts to your existing LSP config
--
-- Requirements:
--   - neovim >= 0.8
--   - nvim-lspconfig plugin
--   - basedpyright language server (npm install -g basedpyright)
--   - ruff_lsp (optional, pip install ruff-lsp)
-- ============================================================================

local M = {}

-- ============================================================================
-- Configuration Options
-- ============================================================================

M.config = {
    -- Auto-detect mayapy (recommended)
    auto_detect_mayapy = true,

    -- Manual override (used if auto_detect_mayapy = false)
    mayapy_path = '/usr/autodesk/maya2024/bin/mayapy',

    -- Maya site-packages path (auto-configured based on mayapy)
    maya_site_packages = nil,

    -- Enable ruff_lsp for linting
    enable_ruff = true,

    -- Debug mode (print extra info)
    debug = false,
}

-- ============================================================================
-- Helper Functions
-- ============================================================================

--- Execute a command and return output
---@param cmd string Command to execute
---@return string Output from command
local function exec(cmd)
    local handle = io.popen(cmd)
    if not handle then
        return ''
    end
    local result = handle:read('*a')
    handle:close()
    return result:gsub('\n$', '')  -- Remove trailing newline
end

--- Check if a file exists and is executable
---@param path string Path to check
---@return boolean True if file exists and is executable
local function is_executable(path)
    return vim.fn.executable(path) == 1
end

--- Detect mayapy installation path
---@return string Path to mayapy or fallback to python3
local function detect_mayapy()
    if M.config.debug then
        print('[DevPyLib] Detecting mayapy installation...')
    end

    -- Try using detect_mayapy.py script
    local script_path = vim.fn.getcwd() .. '/scripts/detect_mayapy.py'
    if vim.fn.filereadable(script_path) == 1 then
        local mayapy = exec('python3 ' .. script_path)
        if mayapy ~= '' and is_executable(mayapy) then
            if M.config.debug then
                print('[DevPyLib] Found mayapy via script: ' .. mayapy)
            end
            return mayapy
        end
    end

    -- Fallback: try common paths by platform
    local system = vim.loop.os_uname().sysname

    local common_paths = {}
    if system == 'Linux' then
        common_paths = {
            '/usr/autodesk/maya2024/bin/mayapy',
            '/usr/autodesk/maya2023/bin/mayapy',
            '/usr/autodesk/maya2022/bin/mayapy',
            '/opt/autodesk/maya2024/bin/mayapy',
        }
    elseif system == 'Darwin' then  -- macOS
        common_paths = {
            '/Applications/Autodesk/maya2024/Maya.app/Contents/bin/mayapy',
            '/Applications/Autodesk/maya2023/Maya.app/Contents/bin/mayapy',
            '/Applications/Autodesk/maya2022/Maya.app/Contents/bin/mayapy',
        }
    elseif system == 'Windows_NT' then
        common_paths = {
            'C:/Program Files/Autodesk/Maya2024/bin/mayapy.exe',
            'C:/Program Files/Autodesk/Maya2023/bin/mayapy.exe',
            'C:/Program Files/Autodesk/Maya2022/bin/mayapy.exe',
        }
    end

    for _, path in ipairs(common_paths) do
        if is_executable(path) then
            if M.config.debug then
                print('[DevPyLib] Found mayapy at: ' .. path)
            end
            return path
        end
    end

    -- Last resort: fallback to system Python
    if M.config.debug then
        print('[DevPyLib] Warning: mayapy not found, using system Python')
    end
    return 'python3'
end

--- Get Maya site-packages path from mayapy
---@param mayapy_path string Path to mayapy
---@return string|nil Path to Maya site-packages
local function get_maya_site_packages(mayapy_path)
    if not is_executable(mayapy_path) then
        return nil
    end

    -- Try to get site-packages from mayapy
    local cmd = mayapy_path .. ' -c "import site; print(site.getsitepackages()[0])" 2>/dev/null'
    local site_packages = exec(cmd)

    if site_packages ~= '' then
        return site_packages
    end

    -- Fallback: infer from mayapy path
    local maya_dir = mayapy_path:match('(.*/maya[^/]*)/bin/mayapy')
    if maya_dir then
        local candidates = {
            maya_dir .. '/lib/python3.10/site-packages',
            maya_dir .. '/lib/python3.9/site-packages',
            maya_dir .. '/lib/python3.11/site-packages',
        }
        for _, path in ipairs(candidates) do
            if vim.fn.isdirectory(path) == 1 then
                return path
            end
        end
    end

    return nil
end

-- ============================================================================
-- LSP Setup Functions
-- ============================================================================

--- Setup basedpyright LSP with mayapy
function M.setup_basedpyright()
    local ok, lspconfig = pcall(require, 'lspconfig')
    if not ok then
        vim.notify('[DevPyLib] nvim-lspconfig not found', vim.log.levels.ERROR)
        return
    end

    -- Detect mayapy path
    local mayapy_path
    if M.config.auto_detect_mayapy then
        mayapy_path = detect_mayapy()
    else
        mayapy_path = M.config.mayapy_path
    end

    -- Get Maya site-packages
    local maya_site_packages = M.config.maya_site_packages
        or get_maya_site_packages(mayapy_path)

    local extra_paths = {}
    if maya_site_packages then
        table.insert(extra_paths, maya_site_packages)
        if M.config.debug then
            print('[DevPyLib] Maya site-packages: ' .. maya_site_packages)
        end
    end

    -- Configure basedpyright
    lspconfig.basedpyright.setup({
        cmd = { 'basedpyright-langserver', '--stdio' },
        filetypes = { 'python' },
        root_dir = lspconfig.util.root_pattern(
            'pyrightconfig.json',
            'pyproject.toml',
            'setup.py',
            'setup.cfg',
            'requirements.txt',
            'Pipfile',
            '.git'
        ),
        single_file_support = true,
        settings = {
            basedpyright = {
                analysis = {
                    autoSearchPaths = true,
                    diagnosticMode = 'workspace',
                    useLibraryCodeForTypes = true,
                    typeCheckingMode = 'basic',
                    extraPaths = extra_paths,
                },
            },
            python = {
                pythonPath = mayapy_path,
                venvPath = vim.fn.getcwd(),
                analysis = {
                    extraPaths = extra_paths,
                },
            },
        },
        capabilities = require('cmp_nvim_lsp').default_capabilities(),
        on_attach = function(client, bufnr)
            -- Print connection info
            vim.notify(
                '[DevPyLib LSP] ' .. client.name .. ' attached\nPython: ' .. mayapy_path,
                vim.log.levels.INFO
            )

            -- Keybindings
            local opts = { noremap = true, silent = true, buffer = bufnr }

            -- Navigation
            vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)
            vim.keymap.set('n', 'gD', vim.lsp.buf.declaration, opts)
            vim.keymap.set('n', 'gi', vim.lsp.buf.implementation, opts)
            vim.keymap.set('n', 'gr', vim.lsp.buf.references, opts)
            vim.keymap.set('n', 'gt', vim.lsp.buf.type_definition, opts)

            -- Documentation
            vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
            vim.keymap.set('n', '<C-k>', vim.lsp.buf.signature_help, opts)

            -- Code actions
            vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, opts)
            vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action, opts)
            vim.keymap.set('n', '<leader>f', vim.lsp.buf.format, opts)

            -- Diagnostics
            vim.keymap.set('n', '[d', vim.diagnostic.goto_prev, opts)
            vim.keymap.set('n', ']d', vim.diagnostic.goto_next, opts)
            vim.keymap.set('n', '<leader>e', vim.diagnostic.open_float, opts)
            vim.keymap.set('n', '<leader>q', vim.diagnostic.setloclist, opts)

            -- Workspace
            vim.keymap.set('n', '<leader>wa', vim.lsp.buf.add_workspace_folder, opts)
            vim.keymap.set('n', '<leader>wr', vim.lsp.buf.remove_workspace_folder, opts)
            vim.keymap.set('n', '<leader>wl', function()
                print(vim.inspect(vim.lsp.buf.list_workspace_folders()))
            end, opts)
        end,
        flags = {
            debounce_text_changes = 150,
        },
    })
end

--- Setup ruff_lsp for fast linting
function M.setup_ruff()
    if not M.config.enable_ruff then
        return
    end

    local ok, lspconfig = pcall(require, 'lspconfig')
    if not ok then
        return
    end

    lspconfig.ruff_lsp.setup({
        on_attach = function(client, bufnr)
            -- Disable hover in favor of basedpyright
            client.server_capabilities.hoverProvider = false

            if M.config.debug then
                print('[DevPyLib] ruff_lsp attached')
            end
        end,
        init_options = {
            settings = {
                -- Ruff settings (matches pyproject.toml)
                args = {
                    '--line-length=100',
                    '--target-version=py310',
                },
            },
        },
    })
end

--- Setup both LSP servers
function M.setup()
    M.setup_basedpyright()
    M.setup_ruff()
end

-- ============================================================================
-- Diagnostic Configuration
-- ============================================================================

--- Configure diagnostic display
function M.setup_diagnostics()
    vim.diagnostic.config({
        virtual_text = {
            prefix = '●',
            source = 'if_many',
        },
        signs = true,
        underline = true,
        update_in_insert = false,
        severity_sort = true,
        float = {
            border = 'rounded',
            source = 'always',
            header = '',
            prefix = '',
        },
    })

    -- Diagnostic signs
    local signs = {
        Error = ' ',
        Warn = ' ',
        Hint = ' ',
        Info = ' ',
    }
    for type, icon in pairs(signs) do
        local hl = 'DiagnosticSign' .. type
        vim.fn.sign_define(hl, { text = icon, texthl = hl, numhl = hl })
    end
end

-- ============================================================================
-- Commands
-- ============================================================================

--- Create user commands for DevPyLib LSP
function M.setup_commands()
    -- Show current Python path
    vim.api.nvim_create_user_command('DevPyLibPythonPath', function()
        local clients = vim.lsp.get_active_clients({ bufnr = 0 })
        for _, client in ipairs(clients) do
            if client.name == 'basedpyright' then
                local python_path = client.config.settings.python.pythonPath
                print('Python path: ' .. python_path)
                return
            end
        end
        print('No basedpyright client active')
    end, {})

    -- Restart LSP
    vim.api.nvim_create_user_command('DevPyLibRestartLSP', function()
        vim.cmd('LspRestart')
    end, {})

    -- Toggle debug mode
    vim.api.nvim_create_user_command('DevPyLibDebug', function()
        M.config.debug = not M.config.debug
        print('DevPyLib debug mode: ' .. tostring(M.config.debug))
    end, {})
end

-- ============================================================================
-- Full Setup (all features)
-- ============================================================================

--- Setup everything (LSP + diagnostics + commands)
function M.setup_all()
    M.setup()
    M.setup_diagnostics()
    M.setup_commands()

    if M.config.debug then
        print('[DevPyLib] Full setup complete')
    end
end

return M
