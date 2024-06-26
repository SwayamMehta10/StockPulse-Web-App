Check out the deployed website: https://stockpulse-h1vy.onrender.com/. 

<h1>About</h1>
<b>StockPulse</b> is a web app to help users who are new to the stock market get an easy understanding of stocks through company banckground, forecast insights and technical analysis along with an AI assitant chatbot. The chatbot can answer all queries related to stock market, technical jargon and also tell you the real time stock prices of companies.

<br>
<h1>Steps</h1>

1. Create a Virtual Environment:
   <br>
   `py -m venv myenv`

2. Activate the virtual environment:
   <br>
   `env/Scripts/activate`

3. Install the required dependencies:
   <br>
   `pip install requirements.txt`

4. Create a **_.env_** file, get a Gemini API key and store it in the file as:
`GOOGLE_API_KEY = ""`

5. Configure Flask to use the _app_ module as the entry point for the application:
   <br>
   `$env:FLASK_APP = "app"`

6. Enable debug mode:
   <br>
   `$env:FLASK_DEBUG = "1"`

7. Run the app:
   <br>
   `flask run`
