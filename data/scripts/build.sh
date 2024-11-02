#!/bin/sh

# Make this script executable
chmod +x "$0"

echo "Repository = $REPO_LINK"
echo "JKS = $JKS_NAME"

# Set paths
JKS_PATH="/data/jks/$JKS_NAME"
CODE_DIR="/data/code"
OUTPUT_DIR="/data/apks"

# Ensure required directories exist
mkdir -p $CODE_DIR $OUTPUT_DIR

# Clone repository
cd $CODE_DIR
git clone $REPO_LINK .
chmod +x gradlew

# Display signing information for debugging
echo "Building project with JKS Path: $JKS_PATH"
echo "Keystore Password: $KEYSTORE_PASSWORD"
echo "Key Alias: $KEY_ALIAS"
echo "Key Password: $KEY_PASSWORD"

# Check for Gradle wrapper and build the project
if [ -f "./gradlew" ]; then
    echo "Gradle wrapper found. Starting build for APK and AAB..."

    # Set up Gradle signing configuration via environment variables for the build
    export ORG_GRADLE_PROJECT_storeFile=$JKS_PATH
    export ORG_GRADLE_PROJECT_storePassword=$KEYSTORE_PASSWORD
    export ORG_GRADLE_PROJECT_keyAlias=$KEY_ALIAS
    export ORG_GRADLE_PROJECT_keyPassword=$KEY_PASSWORD

    # Clean and build APK
    ./gradlew clean assembleRelease -Pandroid.injected.signing.store.file="$JKS_PATH" \
    -Pandroid.injected.signing.store.password="$KEYSTORE_PASSWORD" \
    -Pandroid.injected.signing.key.alias="$KEY_ALIAS" \
    -Pandroid.injected.signing.key.password="$KEY_PASSWORD"

    # ./gradlew clean assembleRelease
    if [ $? -eq 0 ]; then
        echo "APK build completed successfully."
    else
        echo "APK build failed."
        exit 1
    fi

    # Build AAB
    ./gradlew bundleRelease \
        -Pandroid.injected.signing.store.file="$JKS_PATH" \
        -Pandroid.injected.signing.store.password="$KEYSTORE_PASSWORD" \
        -Pandroid.injected.signing.key.alias="$KEY_ALIAS" \
        -Pandroid.injected.signing.key.password="$KEY_PASSWORD"
    # ./gradlew bundleRelease
    if [ $? -eq 0 ]; then
        echo "AAB build completed successfully."
    else
        echo "AAB build failed."
        exit 1
    fi
else
    echo "Gradle wrapper not found. Cannot proceed with build."
    exit 1
fi

# Copy APK and AAB artifacts to mounted volume
if [ -d "app/build/outputs/apk/release" ]; then
    cp app/build/outputs/apk/release/*.apk $OUTPUT_DIR/
    echo "APK files copied to $OUTPUT_DIR"
else
    echo "APK output directory not found."
fi

if [ -d "app/build/outputs/bundle/release" ]; then
    cp app/build/outputs/bundle/release/*.aab $OUTPUT_DIR/
    echo "AAB files copied to $OUTPUT_DIR"
else
    echo "AAB output directory not found."
fi