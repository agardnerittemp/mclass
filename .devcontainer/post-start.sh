#!/bin/bash

DEBUG_VERSION=1

echo "post-start start" >> ~/status

python --version

# this runs in background each time the container starts

# update the base docker images
#docker pull mcr.microsoft.com/dotnet/sdk:5.0-alpine
#docker pull mcr.microsoft.com/dotnet/aspnet:5.0-alpine
#docker pull mcr.microsoft.com/dotnet/sdk:5.0

# Run some logic
# If logic is OK: Send bizevent: OK
# If logic !OK: Send bizevent: error
# cd ..
# output=$(ls -al ~/mclass)
# if [[ $output =~ "test.txt" ]];
# then
#   curl -X POST https://webhook.site/1e9185e3-1225-439b-8381-044fd1f417cc \
#     --header "Content-Type: application/json" \
#     -d "{\"result\": \"$DEBUG_VERSION\": \"YUP\"}"
# else
#   curl -X POST https://webhook.site/1e9185e3-1225-439b-8381-044fd1f417cc \
#     --header "Content-Type: application/json" \
#     -d "{\"result\": \"$DEBUG_VERSION\": \"NOPE\"}"
# fi

# # Finally, destroy the codespace
# #gh codespace delete --codespace $CODESPACE_NAME

echo "post-start complete" >> ~/status