echo building for branch: ${GIT_BRANCH_NAME}
python --version
            
if [ -n "$PYTHON_312_VERSION" ]; then echo "Switching to Python version ${PYTHON_312_VERSION} - using environment var for version"; pyenv global "${PYTHON_312_VERSION}"; fi


python --version
echo printing environment vars
env
echo Extracting stack name from CODEBUILD_INITIATOR
echo $CODEBUILD_INITIATOR
# Extract the second part of CODEBUILD_INITIATOR (stack name)
STACK_NAME=$(echo $CODEBUILD_INITIATOR | cut -d'/' -f2)
echo Stack name is $STACK_NAME
echo $(pwd) 
export WORKING_DIRECTORY=$(pwd)
echo $WORKING_DIRECTORY
# install the main cdk-factory (we'll remove this later - once we publish the package)
pip install -r ./src/requirements.txt
pip install -e .
 # install our example (this will be the main project)
pip install -e ./examples/website/static_website

# change to our samples project
cd ./examples/website/static_website/devops
echo $(pwd) 
echo Installing requirements 
# install requirement
pip install -r requirements.txt 
npx cdk synth {verbose} $STACK_NAME

echo CDK Synth Complete
echo $(pwd) 
echo Listing Files in the sub project folder
ls -la
echo switch back to main path
cd $WORKING_DIRECTORY
echo $(pwd) 
ls -la
echo CDK Synth Complete