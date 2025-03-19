## Information is taken from the below and optimized
https://github.com/neurons-inc/neuronshub-backend/blob/main/neuronshub/common/predict/objectives/detect_image.py
https://github.com/neurons-inc/neuronshub-backend/blob/main/neuronshub/common/predict/objectives/mapping.py
https://github.com/neurons-inc/neuronshub-backend/blob/main/neuronshub/common/image.py

# ML Purpose Detection

This repository contains tools and models for detecting the purpose of assets, such as images and videos, in marketing and advertising contexts. 
The primary goal is to classify assets into categories such as **Brand Building** or **Conversion**, providing detailed insights into their effectiveness and usage.
The responses can be modified to show "reasoning" as well.

## Features

- **Image Detection**:
  - Analyze and classify image/video assets.
  - Determine their purpose: `Brand Building` or `Conversion`.

- **Video Detection**:
  - Process video assets from Google Cloud Storage (GCS).
  - Classify videos based on their marketing purpose.

- **Customizable Models**:
  - Easily extend the detection logic for other asset types.

## Requirements
 - see requirements.txt

### Environment
- Python 3

## Installation

Install the latest package

```
!pip install DetectAssetPurpose
```

If the above Installation Process is not working, consider to use:

```
python3 -m pip install DetectAssetPurpose

```

## Authors
Irina White (i.white@neuronsinc.com)


## Project status
Project is under continuous update and monitoring.