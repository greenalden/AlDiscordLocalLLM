@echo off


echo Installing python

:: Define the directory for Anaconda/Miniconda installation
set ANACONDA_DIR=%~dp0anaconda

:: Define the Miniconda installer URL and filename
set MINICONDA_INSTALLER=miniconda_installer.exe
set MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe

:: Check if Anaconda is already installed
if not exist "%ANACONDA_DIR%" (
    echo Anaconda not found. Installing Miniconda...

    :: Check if curl is available, else use PowerShell to download
    curl --version >nul 2>&1
    if errorlevel 1 (
        echo curl not found. Using PowerShell to download Miniconda...
        powershell -Command "Invoke-WebRequest -Uri %MINICONDA_URL% -OutFile %MINICONDA_INSTALLER%"
    ) else (
        curl -o "%MINICONDA_INSTALLER%" "%MINICONDA_URL%"
    )

    :: Install Miniconda
    start /wait "" "%MINICONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /S /D=%ANACONDA_DIR%
    del "%MINICONDA_INSTALLER%"  :: Delete installer after installation
) else (
    echo Anaconda already installed.
)

:: Set the path to conda
set "PATH=%ANACONDA_DIR%\Scripts;%ANACONDA_DIR%\condabin;%PATH%"

:: Check if 'conda' is recognized
where conda >nul 2>&1
if errorlevel 1 (
    echo Running 'conda init'...
    call conda init
    echo Please restart your Command Prompt and run this script again.
    exit /b
)

:: Force install the specified Python version in the base environment
echo Installing Python 3.11.9 in the base environment...
call conda install python=3.11.9 -y


python -m pip install --upgrade pip



# — General packages —
pip install accelerate==1.5.*
pip install bitsandbytes==0.45.*
pip install colorama
pip install datasets
pip install einops
pip install fastapi==0.112.4
pip install gradio==4.37.*
pip install jinja2==3.1.6
pip install markdown
pip install numba==0.59.*
pip install numpy==1.26.*
pip install pandas
pip install peft==0.15.*
pip install "Pillow>=9.5.0"
pip install psutil
pip install pydantic==2.8.2
pip install pyyaml
pip install requests
pip install rich
pip install safetensors==0.5.*
pip install scipy
pip install sentencepiece
pip install tensorboard
pip install transformers==4.50.*
pip install tqdm
pip install wandb
pip install SpeechRecognition==3.10.0
pip install flask_cloudflared==0.0.14
pip install sse-starlette==1.6.5
pip install tiktoken
pip install discord-py-api

# — CUDA-accelerated wheels —
pip install "https://github.com/oobabooga/llama-cpp-python-cuBLAS-wheels/releases/download/textgen-webui/llama_cpp_python_cuda-0.3.8+cu124-cp311-cp311-win_amd64.whl; platform_system == 'Windows' and python_version == '3.11'"
pip install "https://github.com/oobabooga/llama-cpp-python-cuBLAS-wheels/releases/download/textgen-webui/llama_cpp_python_cuda-0.3.8+cu124-cp311-cp311-linux_x86_64.whl; platform_system == 'Linux' and platform_machine == 'x86_64' and python_version == '3.11'"
pip install "https://github.com/oobabooga/llama-cpp-python-cuBLAS-wheels/releases/download/textgen-webui/llama_cpp_python_cuda_tensorcores-0.3.8+cu124-cp311-cp311-win_amd64.whl; platform_system == 'Windows' and python_version == '3.11'"
pip install "https://github.com/oobabooga/llama-cpp-python-cuBLAS-wheels/releases/download/textgen-webui/llama_cpp_python_cuda_tensorcores-0.3.8+cu124-cp311-cp311-linux_x86_64.whl; platform_system == 'Linux' and platform_machine == 'x86_64' and python_version == '3.11'"
pip install "https://github.com/oobabooga/exllamav3/releases/download/v0.0.1/exllamav3-0.0.1+cu124.torch2.6.0-cp311-cp311-win_amd64.whl; platform_system == 'Windows' and python_version == '3.11'"
pip install "https://github.com/oobabooga/exllamav3/releases/download/v0.0.1/exllamav3-0.0.1+cu124.torch2.6.0-cp311-cp311-linux_x86_64.whl; platform_system == 'Linux' and platform_machine == 'x86_64' and python_version == '3.11'"
pip install "https://github.com/oobabooga/exllamav2/releases/download/v0.2.8/exllamav2-0.2.8+cu124.torch2.6.0-cp311-cp311-win_amd64.whl; platform_system == 'Windows' and python_version == '3.11'"
pip install "https://github.com/oobabooga/exllamav2/releases/download/v0.2.8/exllamav2-0.2.8+cu124.torch2.6.0-cp311-cp311-linux_x86_64.whl; platform_system == 'Linux' and platform_machine == 'x86_64' and python_version == '3.11'"
pip install "https://github.com/Dao-AILab/flash-attention/releases/download/v2.7.4.post1/flash_attn-2.7.4.post1+cu12torch2.6cxx11abiFALSE-cp311-cp311-linux_x86_64.whl; platform_system == 'Linux' and platform_machine == 'x86_64' and python_version == '3.11'"
pip install "https://github.com/oobabooga/flash-attention/releases/download/v2.7.4.post1/flash_attn-2.7.4.post1+cu124torch2.6.0cxx11abiFALSE-cp311-cp311-win_amd64.whl; platform_system == 'Windows' and python_version == '3.11'"

pip install llama-cpp-python




:: End of script
echo Done.
pause