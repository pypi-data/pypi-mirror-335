# Lottie Inline Tool

A simple tool to inline images in Lottie JSON files.

## Installation

```bash
$ pip install lottie-inline
```
## Usage

```bash
$ lottie-inline /path/to/input-lottie-file.json /path/to/output-lottie-file.json
```

## Details

The tool will inline all images in the Lottie JSON file and save the result to the output file.

transform: 

```json
{
  "assets": [
    {
      "id": "image_0",
      "w": 500,
      "h": 500,
      "u": "images/",
      "p": "image.png",
      "e": 0
    },
    //...
  ],
  //...
}
```

to: 

```json
{
  "assets": [
    {
      "id": "image_0",
      "w": 500,
      "h": 500,
      "u": "",
      "p": "data:image/png;base64,...",
      "e": 1
    },
    //...
  ],
  //...
}
```

## License

MIT
