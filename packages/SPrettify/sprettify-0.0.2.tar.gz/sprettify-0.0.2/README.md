# SPrettify

A Python module for formatting and structuring strings efficiently. `SPrettify` helps in creating visually appealing output with alignment, headers, and a clean key-value pairs.

## Features
- Add formatted headers with horizontal tabulation.
- Append lines with custom alignments.
- Create structured key-value pair outputs.
- Print or retrieve the formatted output as a string.

## Installation
This module does not require any external dependencies. Just do `pip install SPrettify` and import it into your project.

## Usage
```python
from SPrettify import Prettify

formatter = Prettify()
formatter.define_alignment(spaces=4)  # Set left alignment

formatter.add_tab("Header", "=", 40)
formatter.add_line("This is a formatted line.")
formatter.add_sort("Key", "Value")

formatter.prettyprint()  # Print output
formatted_string = formatter.prettystring()  # Get output as a string
```

## Methods
### `define_alignment(spaces=0, tabs=0)`
Sets the left alignment with spaces or tabs.

### `add_tab(data="", char="=", lines=30)`
Adds a formatted header with horizontal tabulation.

### `add_line(data="")`
Appends a simple line with the defined alignment.

### `add_sort(key="", value="", separator=":", align=1)`
Formats key-value pairs with custom alignment.

### `prettyprint()`
Prints the formatted output.

### `prettystring()`
Returns the formatted output as a string.

## Found on
This project is used on [GoGoDownloader-R2](https://github.com/Kinuseka/GoGo-Downloader-R2) It can be used as an example of its usage

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

