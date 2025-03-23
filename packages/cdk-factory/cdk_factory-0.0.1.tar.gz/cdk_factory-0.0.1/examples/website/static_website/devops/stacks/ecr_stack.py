from aws_cdk import Stack

from aws_cdk import Duration, RemovalPolicy, aws_ecr
from aws_lambda_powertools import Logger
from constructs import Construct

logger = Logger(__name__)


class ECRStack(Stack):
    """
    Application ECR Stack.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,  # pylint: disable=w0622
        *,
        config: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the domain name
        logger.info("setting up ecr stack")

        self.config = config

        self._setup_ecr_repos()

    def _setup_ecr_repos(self):
        logger.info("Setting erc repos")

        repos = self.config.get("repos", [])
        for repo in repos:
            self.__create_ecr(repo)

    def __create_ecr(self, repo: dict) -> aws_ecr.Repository:
        # Create a new bucket for storing server access logs
        name = repo.get("name")
        empty_on_delete = str(repo.get("empty_on_delete", "false")).lower() == "true"
        image_scan_on_push = (
            str(repo.get("image_scan_on_push", "true")).lower() == "true"
        )
        aws_ecr.Repository(
            scope=self,
            id=name,
            repository_name=name,
            # auto delete images after x days
            # auto_delete_images=self.empty_on_delete,
            # delete images when repo is destroyed
            empty_on_delete=empty_on_delete,
            # scan on push true/false
            image_scan_on_push=image_scan_on_push,
            # removal policy on delete destroy if empty on delete otherwise retain
            removal_policy=(
                RemovalPolicy.DESTROY if empty_on_delete else RemovalPolicy.RETAIN
            ),
        )
