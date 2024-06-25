This provides a webinterface as frontend and a marqo database and OpenAI ChatGPT as backend to ask your eBooks questions.


# Install

## Install WSL
wsl.exe --install --no-distribution

## Install Docker
https://www.docker.com/products/docker-desktop/

## Install python
https://www.python.org/downloads/

If you are using the Windows Installer make sure you check \
[X] Use admin privileges when installing py.exe \
[X] Add python.exe to PATH \
befor you click on "Install Now" \
<img width="200" alt="image" src="https://github.com/OneEyedBlackCatDevelopment/AksYourBooks/assets/173571148/dc7b9373-475d-499f-ba9c-b01893da2396">

## Install python dependencies
pip install marqo
pip install flask
pip install openai
pip install langchain
pip install langchain_openai
pip install PyMuPDF

## Create an API Key for OpenAI (ChatGPT)
The serach function will work without this, but you won't get an AI summery of the results \
https://platform.openai.com/account/api-keys

## Create Environment Variable for OpenAi API Key \
https://platform.openai.com/account/api-keys 
If you want to test your setup without connection to OpenAI, create the environment variable with a space as value
OPENAI_API_KEY

 
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

