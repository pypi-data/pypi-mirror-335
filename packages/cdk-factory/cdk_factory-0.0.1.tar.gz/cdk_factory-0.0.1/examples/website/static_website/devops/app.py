"""
Geek Cafe, LLC
Maintainers: Eric Wilson
MIT License.  See Project Root for the license information.
"""

import os
from pathlib import Path

# import __paths__
from cdk_factory.app import CdkAppFactory


class MyStaticWebSiteApp:
    """My Static WebSite Example"""

    def __init__(self):
        self.name = "MyApp"

    def synth(self):
        """Synth my static web site"""
        print("synth", self.name)
        path = str(Path(__file__).parent)
        config_path = os.path.join(path, "config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(config_path)

        # the CdkAppFactory will use some "canned" or pre-made stacks
        factory: CdkAppFactory = CdkAppFactory(config=config_path)

        # this provides a way to inject stacks from this module
        # stacks: Stacks = Stacks(app=factory.app)
        # stacks.synth()

        # something like this to add to the pipeline(s)
        # factory.pipelines["dev"].stages.add("dev", stack=stacks.stacks)
        cdk_app_file = "./examples/website/static_website/devops/app.py"
        print(
            "👉 Synthing - this runs local and then later in AWS if a self mutate happens"
        )
        print(
            (
                "🚨 Warning - be careful when adding paths.  You don't want to bake in a local path "
                "or a runtime build path that gets carried over into the next build."
            )
        )

        print("synth:synthing path:", cdk_app_file)
        print("synth:file path", __file__)
        print("synth: PWD", os.getenv("PWD"))

        return factory.synth(paths=[path], cdk_app_file=cdk_app_file)


def main():
    """Run the app"""
    app = MyStaticWebSiteApp()
    app.synth()


if __name__ == "__main__":
    main()
