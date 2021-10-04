## Usage:

- Set up your own [Matierals Project](https://materialsproject.org/) account and obtain your own API key from dashboard in head bar of Homepage

- Set the API key into download_data.py MPRester()

- Modify the code in get_bands_info() into the proper data that you want to download

- There's a for loop inside main(), it is inefficient as I don't know the exact mp-ids at the very beginning. But now I think we have pretty much data downloaded, so you can call records_map_ids with setting proper path to raw data. This function will return you a list that stores all mp-ids, so you use this replace original for loop

- Any further questions please contact me
