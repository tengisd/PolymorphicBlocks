# Recommended Setup
1. Clone the edg-v1.5 (https://github.com/lab11/edg-v1.5) and PolymorphicBlocks (https://github.com/BerkeleyHCI/PolymorphicBlocks) repositories
2. Copy .csv files from edg-v1.5\frontend\electronics_lib\resources to PolymorphicBlocks\electronics_lib\resources
3. Install Python 3.7+: https://www.python.org/downloads/
4. Install JDK 15: https://www.oracle.com/java/technologies/javase-jdk15-downloads.html
5. Install IntelliJ: https://www.jetbrains.com/idea/download/
6. Open the PolymorphicBlocks project in IntelliJ
7. In IntelliJ, go to File -> Settings -> Plugins. Install Python Community Edition.
8. In IntelliJ, go to File -> Project Structure -> Project Settings -> Project. Set Project SDK to 15.
9. In IntelliJ, go to File -> Project Structure -> Project Settings -> Modules. Add Python (3.7+).
10. In IntelliJ, go to File -> Project Structure -> Platform Settings -> SDKs. Add Python SDK.
11. Run `pip install protobuf py4j`
12. Run `pip install mypy`
13. Run `pip install --upgrade google-api-python-client`
14. Complete the PolymorphicBlocks Getting Started tutorial: https://github.com/BerkeleyHCI/PolymorphicBlocks/blob/master/getting-started.md