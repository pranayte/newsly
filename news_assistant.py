import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from transformers import pipeline
import pyttsx3

def scrape_news(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        headlines = soup.find_all('h2')

        news_dict = {}

        for index, headline in enumerate(headlines, start=1):
            link_tag = headline.find('a')
            link = link_tag.get('href') if link_tag else 'Link not found'
            absolute_link = urljoin(url, link)

            news_dict[f"Headline {index}"] = {"Label": headline.text.strip(), "Link": absolute_link}

        return news_dict
    else:
        print(f"Failed to retrieve data. Status Code: {response.status_code}")
        return None

if __name__ == "__main__":
    news_url = "https://indianexpress.com/"
    news_data = scrape_news(news_url)

    if news_data:
        for key, value in news_data.items():
            print(f"{key}: {value}")


##### these lib are used for taking audio input from user
# pip install speechrecognition
# pip install pyaudio
# pip install pyttsx3
# Python program to translate
# speech to text and text to speech


import speech_recognition as sr
import pyttsx3 

# Initialize the recognizer 
r = sr.Recognizer() 

# Function to convert text to
# speech
def SpeakText(command):
	
	# Initialize the engine
	engine = pyttsx3.init()
	engine.say(command) 
	engine.runAndWait()
	
	
# Loop infinitely for user to
# speak

def listen():
    print("Speak to capture the input")
    for i in range(0,1):

	# Exception handling to handle
	# exceptions at the runtime
    	try:
		
		# use the microphone as source for input.
    		with sr.Microphone() as source2:
			
			# wait for a second to let the recognizer
			# adjust the energy threshold based on
			# the surrounding noise level 
    			r.adjust_for_ambient_noise(source2, duration=0.2)
			
			#listens for the user's input 
    			audio2 = r.listen(source2)
			
			# Using google to recognize audio
    			MyText = r.recognize_google(audio2)
    			MyText = MyText.lower()

    			print("Did you say ",MyText)
    			SpeakText(MyText)
			
    	except sr.RequestError as e:
    		print("Could not request results; {0}".format(e))
		
    	except sr.UnknownValueError:
    		print("unknown error occurred")
    return MyText


def listen_article():
    Number = None
    print("Speak to capture the input")
    for i in range(0,1):

	# Exception handling to handle
	# exceptions at the runtime
    	try:
		
		# use the microphone as source for input.
    		with sr.Microphone() as source2:
			
			# wait for a second to let the recognizer
			# adjust the energy threshold based on
			# the surrounding noise level 
    			r.adjust_for_ambient_noise(source2, duration=0.2)
			
			#listens for the user's input 
    			audio2 = r.listen(source2)
			
			# Using google to recognize audio
    			Number = r.recognize_google(audio2)
    			Number = Number.lower()

    			print("Did you say ",Number)
    			SpeakText(Number)
			
    	except sr.RequestError as e:
    		print("Could not request results; {0}".format(e))
		
    	except sr.UnknownValueError:
    		print("unknown error occurred")
            
    return Number


def get_news_from_headline(news_dict, headline_label, min_articles=5):
    found = False
    for key, value in news_dict.items():
        if value["Label"].lower() == headline_label.lower():
            found = True
            headline_link = value["Link"]
            articles = scrape_news(headline_link)
            if articles:
                print(f"\nTop News articles from '{value['Label']}':")
                speak_article("News articles from"+value['Label'])
                for i, (label, link) in enumerate(articles.items(), start=1):
                    print(f"{i}.{link['Label']}")
                    speak_article(link['Label'])
                    if i == min_articles:
                        break
                article_number = None
                try:
                    article_name = listen_article()
                    print(article_name)
                    for i, (label, link) in enumerate(articles.items(), start=1):
                        if article_name in link['Label'].lower():
                            article_number=i
                            speak_article("The article"+link['Label']+"says that")
                            print(article_name,article_number)
                        if i == min_articles:
                            break
                    if 1 <= article_number <= min_articles:
                        read_and_summarize_article(articles, article_number)
                        speak_article("Would you like to listen some more articles from the same headline ?, yes or no")
                        articles_repeat=input("Would you like to listen some more articles from the same headline ?, yes or no")
                        if articles_repeat=="yes":
                            get_news_from_headline(news_dict, headline_label, min_articles=5)
                        else:
                            speak_article("Would you like to listen some more articles from new headlines ?, yes or no")
                            headline_repeat=input("Would you like to listen some more articles from new headlines ?, yes or no")
                            if headline_repeat=="yes":
                                headline_function()
                            else:
                                speak_article("Thank you, hope you got the right information. Have a Nice day")
                    else:
                        print("Invalid article number. Please choose a valid number.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            else:
                print("Failed to retrieve news articles.")
            break
    
    if not found:
        print(f"Invalid headline label. Please choose a valid headline label.")

def read_and_summarize_article(articles, article_number):
    article_keys = list(articles.keys())
    if 1 <= article_number <= len(article_keys):
        article_key = article_keys[article_number - 1]
        article_link = articles[article_key]["Link"]

        response = requests.get(article_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_text = soup.find('div', class_='full-details').get_text(strip=True)

            # Summarize the article
            summarized_text = summarize_text(article_text)

            print(f"\nSummarized Article - {article_key}:\n{summarized_text}")

            # Ask for explanation
            speak_article("Do you need an explanation for this article? (yes or no): ")
            explanation_needed = listen_article()

            if explanation_needed == "yes":
                print(f"\nFull Article - {article_key}:\n{article_text}")
                speak_article(article_text)
            else:
                # Read the summarized article using text-to-speech
                print(summarized_text)
                speak_article(summarized_text)
        else:
            print("Failed to retrieve the full article.")
    else:
        print("Invalid article number. Please choose a valid number.")

def summarize_text(text):
    summarizer = pipeline("summarization")
    summarized_text = summarizer(text, max_length=150, min_length=50, length_penalty=2.0, num_beams=4)[0]['summary_text']
    return summarized_text

def speak_article(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def headline_function():
    headline_number={}
    for headline,label_name in news_data.items():
        headline_number[headline]=label_name['Label']
        print(headline,label_name['Label'])
    speak_article("Today news labels are.")
    speak_article(list(headline_number.values()))
    speak_article("What is the label you need to listen?")
    headline_label = listen()
    get_news_from_headline(news_data, headline_label)


try:
    speak_article("Good morning, I\'m newsly, I\'m here to help you to listen today\'s news")
    headline_function()
except ValueError:
    print("Invalid input. Please enter a valid label.")