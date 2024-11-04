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
#!/bin/sh



# Construct REPO_LINK with authentication if credentials are provided
if [ -n "$BITBUCKET_USERNAME" ] && [ -n "$BITBUCKET_APP_PASSWORD" ]; then
    # Use username and app password for authentication
    AUTHENTICATED_REPO_LINK=$(echo "$REPO_LINK" | sed "s|https://|https://$BITBUCKET_USERNAME:$BITBUCKET_APP_PASSWORD@|")
elif [ -n "$BITBUCKET_OAUTH_TOKEN" ]; then
    # Use OAuth token for authentication by replacing any username with x-token-auth
    AUTHENTICATED_REPO_LINK=$(echo "$REPO_LINK" | sed "s|https://[^@]*@|https://x-token-auth:$BITBUCKET_OAUTH_TOKEN@|")
else
    # Use REPO_LINK directly if no credentials are provided
    AUTHENTICATED_REPO_LINK=$REPO_LINK
fi

# Display the authenticated repo link for debugging (ensure no sensitive data in logs)
echo "AUTHENTICATED_REPO_LINK=$AUTHENTICATED_REPO_LINK"

# Check if the user provided a branch
if [ -n "$BRANCH_NAME" ]; then
    echo "Pulling code from branch $BRANCH_NAME"
    git clone -b "$BRANCH_NAME" --single-branch "$AUTHENTICATED_REPO_LINK" .
else
    echo "Pulling code from Git"
    git clone "$AUTHENTICATED_REPO_LINK" .
fi



chmod +x gradlew
# yes | sdkmanager --licenses

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


# docker run --rm -v "$(pwd)/Apks:/data/apks" test
# docker run --rm -v "$(pwd)/Apks:/data/apks" -v "$(pwd)/gradle_cache:/root/.gradle" -v "$(pwd)/android_sdk:/opt/android-sdk" test
# docker run --rm -v "$(pwd)/android_sdk:/opt/android-sdk" -it test /bin/bash -c "\
    #  yes | sdkmanager --licenses --sdk_root=/opt/android-sdk"

# Final
# docker run --rm -v "$(pwd)/Apks:/data/apks" -v "$(pwd)/gradle_cache:/root/.gradle" -v "$(pwd)/android_sdk:/opt/android-sdk" test /bin/bash -c "yes | sdkmanager --licenses --sdk_root=/opt/android-sdk && ./scripts/build.sh"


# docker run --rm -v "$(pwd)/Apks:/data/apks" -v "$(pwd)/gradle_cache:/root/.gradle" test