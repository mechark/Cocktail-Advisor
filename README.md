# Cocktail-Advisor 👨‍💼
The app was built with fun and pleasure in ~3 hours 😊

It has a simple UI and uses gemini-1.5-pro to present you with nice advices on cocktails from [Cocktails dataset](https://www.kaggle.com/datasets/aadyasingh55/cocktails). 

![image](https://github.com/user-attachments/assets/7d047998-274b-4f0f-b63e-389ed832dc6e)

# How to run it

### Install dependencies

Simply run `uv init` from the root directory

### Start Frontend server

At the root directory of the project run the following command:
`python -m http.server $port`
This will start the UI server

Head to `http://localhost:$port/` to see the UI!

### Start Backend server 

At the root directory of the project run the following command:
`uvicorn app.main:app --host 0.0.0.0 --port 80`

This will start the backend server

**Now you can type in your question and cocktail advisor will respond!**
