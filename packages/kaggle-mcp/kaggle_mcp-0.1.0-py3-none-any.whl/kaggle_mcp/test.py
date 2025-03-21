from pathlib import Path
from kaggle_mcp.utils import download_dataset
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi

competition_id = "playground-series-s5e3"
data_dir = Path(__file__).parent / "data" / competition_id


# api = KaggleApi()
# api.authenticate()
# print(api.model_list_cli())
# from pprint import pprint
# pprint(api.competitions_list(search="spaceship-titanic"))
# # api.competition_download_files(
# #     competition=competition_id,
# #     path=data_dir,
# #     quiet=False,
# #     force=False,
# # )


download_dataset(competition_id, data_dir)