This provides a webinterface as frontend and a marqo database and OpenAI ChatGPT as backend to ask your eBooks questions.


# Install

## Install WSL
wsl.exe --install --no-distribution

## Install Docker
https://www.docker.com/products/docker-desktop/

## Intall python
https://www.python.org/downloads/

If you are using the Windows Installer make sure you check \
[X] Use admin privileges when installing py.exe \
[X] Add python.exe to PATH \
befor you click on "Install Now" \
<img width="200" alt="image" src="https://github.com/OneEyedBlackCatDevelopment/AksYourBooks/assets/173571148/dc7b9373-475d-499f-ba9c-b01893da2396">

 
## Setup marqo.ai
https://docs.marqo.ai/2.8

Open PowerShell and type the following command. This may take some time.
\
docker pull marqoai/marqo:latest
\
\
Then type: \
docker run --name marqo -it -p 8882:8882 marqoai/marqo:latest
\
Now you should have a marqo container running on port 8882. This is how it looks in Docker Desktop: \
<img width="200" alt="image" src="https://github.com/OneEyedBlackCatDevelopment/AksYourBooks/assets/173571148/7b68541c-1ae1-4523-8735-788d0eca55d0">

