# YouTube Gender Polarization Study

This repository contains the source code used for the research project of YouTube recommendation algorithm on gender polarization. The report can be found [here](https://docs.google.com/document/d/1_1yvzVqZLIstgZnC3qM0xkpkHDblUdICsD8keyV1xGk/edit?usp=sharing).

# Installing / Getting started

To run `search_scraper.py`, use the following dependencies:
```
selenium==3.141.0
undetected-chromedriver==3.1.0
```
You will also need to download Chrome and [chromedriver](https://chromedriver.chromium.org/downloads) and specify the version at creation of driver.

e.g. Using Chrome version 106, you need to download a compatible Chromedriver that starts with 106. Then you need to specify the driver path and version.
```
uc.Chrome(executable_path=DRIVER_PATH, version_main=106)
```

To run `travers_video.py`, in addition of installing selenium and undetected-chromedriver, you also need to [have access to YouTube API](https://developers.google.com/youtube/v3/getting-started) and replace `DEVELOPER_KEY`, `YOUTUBE_API_SERVICE_NAME` and `YOUTUBE_API_VERSION` with your own information. 



# Related projects

Studies siloing effect of political content on YouTube by Mika Desblancs: https://github.com/mika-jpd/YouTube_Radicalization_Recommendations
