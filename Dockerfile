FROM ubuntu:latest

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    openjdk-17-jdk \
    gradle \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"
ENV PROJECT_NAME="ishfaq"

# Define Android SDK root
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

# Download and set up Android SDK
RUN mkdir -p $ANDROID_HOME/cmdline-tools && \
    cd $ANDROID_HOME/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip commandlinetools-linux-9477386_latest.zip -d $ANDROID_HOME/cmdline-tools && \
    rm commandlinetools-linux-9477386_latest.zip && \
    mkdir -p $ANDROID_HOME/cmdline-tools/latest && \
    mv $ANDROID_HOME/cmdline-tools/cmdline-tools/* $ANDROID_HOME/cmdline-tools/latest && \
    yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"

WORKDIR /data

# Set environment variables for keystore
ENV JKS_NAME=ishfaq.jks
ENV KEYSTORE_PASSWORD=ishfaq
ENV KEY_PASSWORD=ishfaq
ENV KEY_ALIAS=ishfaq

# ENV SCRIPT=build_github.sh
ENV SCRIPT=build_bitbucket.sh
ENV REPO_LINK="https://github.com/developwithishfaq/ishfaq-test"

# Create necessary directories
RUN mkdir -p ./jks ./scripts ./code

# Copy the keystore and script into the image
COPY ./data/keys/$JKS_NAME ./jks/
COPY ./data/scripts/$SCRIPT ./scripts/

# Make the script executable
RUN chmod +x ./scripts/$SCRIPT

# Set entrypoint to the build script
ENTRYPOINT ["/bin/sh", "-c", "./scripts/$SCRIPT"]
