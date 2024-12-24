import pandas as pd
from openai import OpenAI
import os
import recs
import random

class AdAutomation:
    def __init__(self):
        # Initialize any required variables or objects
        self.client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    def get_user_history(self, user_id):
        """
        Retrieve user history based on user_id from events_df.
        :param user_id: ID of the user
        :return: Dictionary containing user interaction history
        """
        # Get all events for the user
        events_df = pd.read_csv('./synthetic-browsing-history/events_df.csv')
        user_events = events_df[events_df["User_id"] == user_id]

        # Extract ads with specific interaction scores
        clicked_ads = user_events[user_events["Interaction_score"] == 2][
            ["Interaction_score", "product_name", "product_category"]
        ]
        converted_ads = user_events[user_events["Interaction_score"] == 4][
            ["Interaction_score", "product_name", "product_category"]
        ]

        # Combine data into user history
        user_history = {
            "user_id": user_id,
            "clicked_ads": clicked_ads,
            "converted_ads": converted_ads,
            "all_interactions": user_events[
                ["Interaction_score", "product_name", "product_category"]
            ],
        }
        return user_history

    def automate_ad(self, ad_data, user_id):
        """
        Automate ad processing logic.
        :param ad_data: The top 5 recommended ads
        :param user_id: The user in need of an ad
        """

        client = self.client
        history = self.get_user_history(user_id)

        clicked_ads = history['clicked_ads']
        converted_ads = history['converted_ads']

        prompt = f"""
                Below are the top 5 ads recommended for the user:
                {ad_data}

                User interaction history:
                - Clicked Ads: {clicked_ads}
                - Converted Ads: {converted_ads}

                Considering the ads provided, pick the best one based on the user's interactions. 
                Interaction_score is defined as follows: {{skipped: 0, impression: 1, click: 2, conversion: 4}}. 
                
                Create an ad for an accessory or complementary product to something the user has successfully converted, 
                or generate an ad for one of the top 5 ads that the user clicked on, 
                Make the ad engaging, persuasive, and exciting.

                Example of an ad:
                Unlock your creative potential with Canva! Design stunning graphics, presentations, and social media posts with ease, 
                even if you have no design experience. Our intuitive drag-and-drop interface, combined with a treasure trove of templates and elements, 
                makes it simple to bring your ideas to life. Whether you're promoting your business, preparing for an event, or just want to share 
                something fabulous with friends, Canva is your go-to design partner. Join millions of satisfied users and try Canva for free today—your masterpiece is just a click away!
                """
        
        completion = client.chat.completions.create(
            model = 'gpt-4o-mini',
            messages=[
                {"role": "system", "content": "You are an ad creator for spotify, this ad will be put into speech to text, so be energetic."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_content = completion.choices[0].message.content
        with open('chatGPT_Response.txt', 'a') as file:
            file.write(f'prompt: {prompt}\nresponse: {response_content}')

        print(response_content)
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
            response.write_to_file("Test_Output.mp3")
            print("Audio saved as Test_Output.mp3")
        except Exception as e:
            print(f"Error in text-to-speech: {e}")



    def main(self):
        """
        Main method to execute the workflow.
        """
        user_id = random.randint(1, 99)
        device_type = random.choice(['mobile', 'tablet', 'desktop'])
        ad_rec = recs.Similar_Users().recommend_ads(user_id, device_type)
        ad_response = self.automate_ad(ad_rec, user_id)
        # text_to_speech = self.text_to_speech(ad_response)


# Example usage
if __name__ == "__main__":
    ad_automation = AdAutomation()
    ad_automation.main()