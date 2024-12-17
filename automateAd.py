import pandas as pd
import json
from openai import OpenAI
import os


class AdAutomation:
    def __init__(self):
        # Initialize any required variables or objects
        self.client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    def getUserData(self, user):
        """
        Reads user browsing data from CSV, converts to JSON, and returns the JSON data.
        :param user: User ID or identifier
        :return: JSON representation of the user's data
        """
        df = pd.read_csv(f'./synthetic-browsing-history/Israel/synthetic-browsing-history-IL_{user}.csv')

        # Filter rows where 'original_content' is 'Shopping'
        df_targeted = df[df['original_content'] == 'Shopping']

        # Extract domain names and count visits
        df['domain'] = df['synthetic_url'].apply(lambda x: x.split('/')[2])  # Extract domain from URL
        top_3_websites = df['domain'].value_counts().head(3).to_dict()  # Top 3 websites and their counts

        # Convert filtered 'Shopping' content to JSON
        json_data = df_targeted.to_json(orient='records', indent=4)

        # Save filtered data to a file
        with open(f'./userData/user_{user}_data.json', 'w') as json_file:
            json_file.write(json_data)

        # Return both the filtered data and top 3 websites
        result = {
            "filtered_data": json.loads(json_data),  # Filtered JSON data
            "top_3_websites": top_3_websites         # Top 3 websites and their counts
        }
        return result

    def automate_ad(self, ad_data):
        """
        Automate ad processing logic.
        :param ad_data: The ad data to process
        """
        # Add logic to automate ads
        client = self.client
        prompt = (f'''Below is browsing information about a user and the top 3 websites that the user visited: ${ad_data}
                    
                    
                    based on the user's browser history and all you know about him, create an ad in a paragraph for only the number 1 website he visited. Make sure the website is in the JSON file under top_3_websites. 
                    The ad should be engaging, persuasive, and exciting. Make sure the ad includes a product related call to action to the audience. 
                ''')

        completion = client.chat.completions.create(
            model = 'gpt-4o-mini',
            messages=[
                {"role": "system", "content": "You are an ad creator."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_content = completion.choices[0].message.content
        with open('chatGPT_Response.txt', 'w') as file:
            file.write(f'prompt: {prompt}\nresponse: {response_content}')

        return response_content

    def speech_to_text(self, audio):
        """
        Convert speech audio to text.
        :param audio: Audio file or audio stream
        :return: Transcribed text
        """
        # Add logic for speech-to-text conversion
        pass

    def text_to_speech(self, text):
        """
        Convert text to speech.
        :param text: Text to convert to audio
        :return: Audio data or file
        """
        # Add logic for text-to-speech conversion
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text,
            )
            response.stream_to_file("Test_Output.mp3")
            print("Audio saved as Test_Output.mp3")
        except Exception as e:
            print(f"Error in text-to-speech: {e}")

    def main(self):
        """
        Main method to execute the workflow.
        """
        # Example workflow:
        user_data = self.getUserData(4)
        # print(json.dumps(user_data, indent=4))
        ad_response = self.automate_ad(user_data)
        # print("Generated Ads:", ad_response)
        text_to_speech = self.text_to_speech(ad_response)


# Example usage
if __name__ == "__main__":
    ad_automation = AdAutomation()
    ad_automation.main()