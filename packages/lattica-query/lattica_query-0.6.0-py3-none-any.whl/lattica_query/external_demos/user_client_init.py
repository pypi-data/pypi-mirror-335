from lattica_query import hom_common
from lattica_common.app_api import LatticaAppAPI
from lattica_query.worker_api import LatticaWorkerAPI

# TODO (pavel): this script is not up to date and won't work!
worker_api_client = LatticaWorkerAPI("<YOUR-TOKEN-HERE>")
app_client = LatticaAppAPI("<YOUR-TOKEN-HERE>")

hom_common.user_client_init(
    worker_api_client,
    app_client,
    secret_key_file_path='my_secret_key.lsk',
)

