# Usage of python shell

1. Once you clone the repository, navigate to the `python` directory:

   ```bash
   cd 15 - shell/python
   ```

2. run the command below to create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

5. Now, crun the command

```
python -m pip install --editable .
```

This allows you to install the package in editable mode, so any changes you make to the code will be reflected without needing to reinstall.

6. You can now run the Python shell by executing:
   ```bash
   ./ccsh
   ```
