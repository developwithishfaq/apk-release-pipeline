
echo "Repository = $REPO_LINK"
echo "Jks = $JKS_NAME"

JKS_PATH="/data/jks/$JKS_NAME"
# Create a directory for the code
CODE_DIR="/data/code"

# Create the directory if it doesn't exist
mkdir -p $CODE_DIR

# Move into the code directory
cd $CODE_DIR

git clone $REPO_LINK

