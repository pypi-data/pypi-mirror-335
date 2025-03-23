import aws_cdk
from aws_cdk import Stack
from static_website.devops.stacks.ecr_stack import ECRStack


class Stacks:
    def __init__(self, app: aws_cdk.App):
        self.app = app
        self.stacks = []

    def __load_stacks(self):
        """
        Loads the stacks
        """

        ecr_stack_config = {
            "repos": [
                {
                    "name": "app_x_repo",
                    "type": "ecr",
                    "description": "ECR Repository",
                    "enabled": True,
                    "image_scan_on_push": True,
                    "empty_on_delete": True,
                },
                {
                    "name": "app_y_repo",
                    "type": "ecr",
                    "description": "ECR Repository",
                    "enabled": True,
                    "image_scan_on_push": True,
                    "empty_on_delete": True,
                },
            ]
        }

        ECRStack(scope=self.app, id="ecr", config=ecr_stack_config)

    def synth(self):
        """
        Synthesize the stacks
        """
        print("synthing")
        self.__load_stacks()
