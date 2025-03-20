# Touch's Brainf**k Interpreter!

## Installation
- ### From Source:
  - #### Windows:
    - Run `test.bat` for easy installation!
  - #### Others (Mac & Linux):
    - The code block below should work in your terminal:
    - ```sh
      python setup.py sdist bdist_wheel

      pip install .
      ```
- ### From PyPI:
  - #### With PIP:
    -  Run `pip install touch-brainf` in your terminal
      
## Using the Interpreter
- ### From the terminal:
  - Run `touch-brainf <filename>` in your terminal
  - If that doesn't work, use `python -m touch_brainf <filename>`
- ### In a Python File:
  - The `main.py` file is an example of a way to use the package in a Python file. The example below is a very simple example.
  - ```py
    import touch_brainf as bf

    runner = bf.Runner("+++.")
    runner.run()
    ```
  - I don't know why someone would do this, but it's their choice
 
## Uninstallation
Just run `pip uninstall touch-brainf`!

-----

<img src="https://github.com/user-attachments/assets/555c8916-9614-472c-ab8d-d4c2bf7aa1e4" alt="sonic drawing" width="470"/>
