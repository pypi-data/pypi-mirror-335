import os
from urllib.parse import urljoin

from aw_client.exceptions import AwClientMisconfigured


class MlflowWrapper:
    """ """
    def __init__(self, aw_url: str, auth_token: str):
        """ """
        self.aw_url = aw_url
        self.auth_token = auth_token
        self.mlflow = None

    def _mlflow(self):
        """ """
        if not self.mlflow:
            try:
                import mlflow
            except ImportError:
                raise AwClientMisconfigured(
                    'Для использованиея MLFlow установите библиотеку с опцией ml: pip install analytic-workspace-client[ml]')
            
            if not self.auth_token:
                data_master_url = urljoin(self.aw_url, 'data-master/get-token')
                raise AwClientMisconfigured(
                    f'Не указан токен доступа к AnalyticWorkspace. Пройдите по адресу {data_master_url} для получения '
                    f'токена.')
            
            tracking_url = urljoin(self.aw_url, 'mlflow')

            if mlflow.get_tracking_uri() != tracking_url:
                mlflow.set_tracking_uri(tracking_url)

            os.environ['MLFLOW_TRACKING_TOKEN'] = self.auth_token
            self.mlflow = mlflow

        return self.mlflow

    def setup_experiment(self, experiment_name: str) -> str:
        """ """
        mlflow = self._mlflow()

        experiment = mlflow.get_experiment_by_name(experiment_name)
        return mlflow.create_experiment(experiment_name) if experiment is None else experiment.experiment_id

    def __getattr__(self, name: str):
        """ """
        mlflow = self._mlflow()
        return getattr(mlflow, name)