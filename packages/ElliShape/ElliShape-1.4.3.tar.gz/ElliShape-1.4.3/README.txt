### Detailed Steps for Installation and Usage of ElliShape

#### Preparation Steps:
Option 1. Install Conda (if not already installed):
    - Download Anaconda from the official website:
      https://www.anaconda.com/
    - Follow the installation instructions for your operating system

Option 2. Install Python (if not using Conda):
    - Download Python 3.10 or later from the official website: https://www.python.org/downloads/ 
    - Follow the installation instructions and ensure you select the option to add Python to your system PATH

#### Installation and Usage with Conda:
1. Open the Anaconda Prompt 
2. Create a Conda environment with Python 3.10:
    ```Anaconda Prompt
    conda create -n ElliShape python=3.10
    ```
3. Activate the environment:
    ```Anaconda Prompt
    conda activate ElliShape
    ```
4. Install the ElliShape package:
    ```Anaconda Prompt
    pip install  path/to/ElliShape-1.3.0-py3-none-any.whl
    ```
4. Download the required model weight files:
    ```Anaconda Prompt
    python path/to/download_pth.py
    ```
5. Run ElliShape:
    ```Anaconda Prompt
    ElliShape
    ```

#### Direct Installation with Python Environment (Requires Python >= 3.10):
1. Open the Command Prompt
2. Install the ElliShape package:
    ```cmd
    pip install  path/to/ElliShape-1.3.0-py3-none-any.whl
    ```
3. Download the required model weight files:
    ```cmd
    python path/to/download_pth.py
    ```
4. Run ElliShape:
    ```cmd
    ElliShape
    ```

#### Notes:
- Ensure your environment meets the Python version requirements.
- The model weight files are essential for running ElliShape. Make sure to download them before using the software.
- For detailed documentation and troubleshooting, refer to the official website or contact support.






