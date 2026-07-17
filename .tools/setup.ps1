# === CONFIGURATION ===
$PYTHON_EXE = "python.exe"
$VENV_NAME = ".venv"
$VENV_PATH = Join-Path -Path "." -ChildPath $VENV_NAME
$VENV_PYTHON = Join-Path -Path $VENV_PATH -ChildPath "Scripts\python.exe"
$ACTIVATE_SCRIPT = Join-Path $VENV_PATH "Scripts\Activate.ps1"
$PY_VERSION = "3.13"

$PY_REQS = ".\requirements.txt"

# === PYTHON CHECK ===
function IS-PYTHON-INSTALLED {
    Write-Host "Checking for Python v$PY_VERSION..." -ForegroundColor Cyan

    try {
        $output = & py -$PY_VERSION -m pip --version 2>&1

        if ($output -match "No suitable Python runtime|Pass --list|Microsoft Store") {
            Write-Host "py launcher failed to locate Python $PY_VERSION." -ForegroundColor Yellow
            throw "Launcher fallback"
        }

        Write-Host "Python $PY_VERSION found via py launcher." -ForegroundColor Green
        return $true
    } catch {
        Write-Host "py -$PY_VERSION failed. Trying python.exe..." -ForegroundColor Yellow
        try {
            $OUTPUT = & $PYTHON_EXE --version 2>&1
            if ($OUTPUT -match "Python ($PY_VERSION)\.") {
                Write-Host "Python $PY_VERSION found via python.exe." -ForegroundColor Green
                return $true
            } else {
                Write-Host "Python is installed, but not version $PY_VERSION. Found: $OUTPUT" -ForegroundColor Yellow
                return $false
            }
        } catch {
            Write-Host "Python not found via PATH or py launcher." -ForegroundColor Red
            return $false
        }
    }
}

# === INSTALL PYTHON ===
function INSTALL-PYTHON {
    $INSTALLER_URL = "https://www.python.org/ftp/python/$PY_VERSION.0/python-$PY_VERSION.0-amd64.exe"
    $INSTALLER_PATH = "$env:TEMP\python-$PY_VERSION.0-amd64.exe"

    Write-Host "Downloading Python $PY_VERSION installer..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $INSTALLER_URL -OutFile $INSTALLER_PATH

    Write-Host "Running installer..." -ForegroundColor Cyan
    Start-Process -FilePath $INSTALLER_PATH -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait

    Write-Host "Python $PY_VERSION installation completed." -ForegroundColor Green
}

# === CHECK PYTHON OR PROMPT TO INSTALL ===
if (-not (IS-PYTHON-INSTALLED)) {
    $USER_INPUT = Read-Host "Python $PY_VERSION is not installed. Download and install now? (y/n)"
    if ($USER_INPUT -match '^[Yy]$') {
        INSTALL-PYTHON

        # Re-run this script in a new shell after install
        $CURRENT_SCRIPT = $MyInvocation.MyCommand.Path
        Write-Host "Re-running script in new shell to continue setup..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy Bypass", "-File `"$CURRENT_SCRIPT`""
        exit
    } else {
        Write-Host "Installation aborted by user." -ForegroundColor Red
        exit 1
    }
}

# === VENV SETUP ===
Write-Host "Checking for virtual environment at $VENV_PATH ..." -ForegroundColor Cyan
if (-Not (Test-Path $VENV_PYTHON)) {
    Write-Host "Virtual environment not found. Creating venv..." -ForegroundColor Yellow
    py -$PY_VERSION -m venv $VENV_NAME

    if (-Not (Test-Path $VENV_PYTHON)) {
        Write-Host "Error: venv creation failed. Could not find $VENV_PYTHON" -ForegroundColor Red
        exit 1
    }

    Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
    & $VENV_PYTHON -m pip install --upgrade pip==25.3
    & $VENV_PYTHON -m pip install -r $PY_REQS
} else {
    Write-Host "Virtual environment found." -ForegroundColor Green
}

# === ACTIVATE AND RUN ===
if (Test-Path $ACTIVATE_SCRIPT) {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    . $ACTIVATE_SCRIPT

    pip uninstall -y snowstream-cli
    python -m build ./src
    pip install -e src
} else {
    Write-Host "Error: Could not find venv activation script." -ForegroundColor Red
    exit 1
}
