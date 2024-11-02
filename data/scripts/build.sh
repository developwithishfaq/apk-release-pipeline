
echo "Repository = $REPO_LINK"
echo "Jks = $JKS_NAME"

JKS_PATH="/data/jks/$JKS_NAME"
# Create a directory for the code
CODE_DIR="/data/code"

# Create the directory if it doesn't exist
mkdir -p $CODE_DIR

# Move into the code directory
cd $CODE_DIR

git clone $REPO_LINK .
chmod +x gradlew
echo "building project"
if [ -f "./gradlew" ]; then
    # If a Gradle wrapper is present, assume it's an Android project
    export ORG_GRADLE_PROJECT_storeFile=$JKS_PATH
    export ORG_GRADLE_PROJECT_storePassword=ishfaq
    export ORG_GRADLE_PROJECT_keyAlias=ishfaq
    export ORG_GRADLE_PROJECT_keyPassword=ishfaq

    # Run the build command for a signed APK
    ./gradlew assembleRelease
    echo "Android build and signing completed successfully."
else
    echo "Failed to build"
fi





