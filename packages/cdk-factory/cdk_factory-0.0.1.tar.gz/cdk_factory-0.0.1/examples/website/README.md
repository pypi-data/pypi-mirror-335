# WebSite Pipeline

This sample deploys an AWS CodePipeline, which will do the following

1. Builds the AWS CodePipeline
2. Connects to a repo like GitHub, AWS CodeCommit, etc
3. The first time this is runs CodePipeline also runs
4. Subsequent check-ins will run the Pipeline