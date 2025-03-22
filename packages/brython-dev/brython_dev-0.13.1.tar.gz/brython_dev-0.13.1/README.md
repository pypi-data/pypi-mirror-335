# Brython-dev

Brython-dev is a Python library for developers in brython.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
pip install brython-dev
```

## Usage

For runserver

```bash
py -m brython_dev run
```

## Configuration

The configuration is in the filename `brython.yml`

* **name**: String. The name of the proyect
* **proyect**: String, Default: `Path(name)`. The path of the proyect
* **app**: String, Default: `app.py`, `null` to disable. The python main filename
* **template**: String, Default: `app.html`, `null` to disable. The html main template
* **proyect_tests**: String, Default: `Path(tests)`. The path of the proyect tests
* **app_tests**: String, Default: `app.py`, `null` to disable. The python tests main filename
* **template_tests**: String, Default: `app.html`, `null` to disable. The html tests main template
* **console**: Boolean, Default: `false`. Enable the console in the navegator
* **metatags**: List. A list whith meta tags
* **stylesheets**: List. A list whith extras stylesheets
* **extensions**: Dict. A dict whith enable brython extensions
  * **brython**: Boolean, Default: `true`. Enable the brython library
  * **brython_stdlib**: Boolean, Default: `false`. Enable the brython stdlib library
* **scripts**: List. A list whith extras scripts
* **pyscripts**: List. A list whith extras python scripts
* **brython_url_prefix**: String, Default: `/`. The brython.js and brython_stdlib.js url prefix
* **brython_options**: Dict. A dict whith brython options

## License
[MIT](https://choosealicense.com/licenses/mit/)