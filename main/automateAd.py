import pandas as pd
from openai import OpenAI
import os
from recs import Similar_Users
import random
from datetime import datetime
from elevenlabs.client import ElevenLabs
# from pydub import AudioSegment
import ffmpeg
import time

class AdAutomation:
    def __init__(self):
        # Initialize any required variables or objects
        self.OPENclient = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
        self.ELABSclient = ElevenLabs(api_key = os.getenv("ELEVENLABS_API_Key"))
        self.musicList = ['../music/BestPart.mp3', '../music/WildFlower.mp3']

    def get_user_history(self, user_id):
        """
        Retrieve user histx ory based on user_id from events_df.
        :param user_id: ID of the user
        :return: Dictionary containing user interaction history
        """
        # Get all events for the user
        events_df = pd.read_csv('../Data/events_df.csv')
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

        client = self.OPENclient
        history = self.get_user_history(user_id)

        clicked_ads = history['clicked_ads']
        converted_ads = history['converted_ads']

        prompt = f"""
                    Using the following data:
                    User Profile:
                    Clicked Ads: {clicked_ads}
                    Converted Ads: {converted_ads}

                    Top 5 Recommended Ads:
                    {ad_data}

                    Create a personalized, engaging, and memorable audio ad tailored to the user's interaction history. Follow these instructions:
                    Personalization
                    Prioritize creating an ad for a complementary product related to a successfully converted item.
                    Alternatively, create an ad for one of the top 5 ads the user clicked on.
                    Speak directly to the listener in a conversational, relatable tone.
                    Structure and Clarity
                    Mention the brand or product immediately within the first sentence (max 25 characters for the name).
                    Highlight the benefits and value proposition clearly and concisely.
                    Conclude with a clear call-to-action (CTA):
                    CTA options:
                    Apply now | Book now | Buy now | Buy tickets | Click now | Download | Find stores | Get coupon | Get info | Learn more | Listen now | More info | Pre-save | Save now | Share | Shop now | Sign up | Visit profile | Visit site | Watch now
                    Technical Requirements
                    Limit the ad to 250 characters (or 60-80 words for a 30-second ad).
                    Use simple, real-life language without emojis.
                    Keep everything lowercase.
                    Creative Elements
                    
                    Examples of Good Ads
                    Grammarly:
                    "Want to write confidently, anywhere? Grammarly helps you communicate clearly with tone suggestions and real-time grammar fixes. Download Grammarly for free today and let your words shine!"
                    Headspace:
                    "Stressed out? Find your calm with Headspace. Guided meditations and mindfulness made simple. Start your free trial now and discover a healthier, happier you."
                    Deliver a polished, user-centered ad script that adheres to the guidelines above and leaves a lasting impression on the listener.
                """
        
        completion = client.chat.completions.create(
            model = 'gpt-4o',
            messages=[
                {"role": "system", "content": """
                    You are an expert audio ad creator for Spotify. Your task is to craft short, engaging, and persuasive ad scripts that will be converted into speech. 
                    These ads must sound conversational, energetic, and tailored to the listener's preferences and interaction history.
                    Follow these rules:
                    Mention the brand or product name within the first sentence.
                    Highlight the key benefits or value of the product.
                    Conclude with a clear call-to-action from the provided options.
                    Limit the script to 200 characters and keep everything lowercase.
                    Focus on making the ad:
                    Memorable, easy to understand, and impactful.
                    Authentic and enthusiastic, leaving a lasting impression on the listener.
                 """},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.6
        )

        response_content = completion.choices[0].message.content
        with open('../chatGPT_Response.txt', 'a') as file:
            file.write(f'prompt: {prompt}\nresponse: {response_content}')

        # print(response_content)

        # returned_list = []
        # returned_list.append(response_content)
        # returned_list.append()
        return response_content

    def speech_to_text(self, audio):
        """
        Convert speech audio to text.
        :param audio: Audio file or audio stream
        :return: Transcribed text
        """
        # Add logic for speech-to-text conversion
        pass

    def text_to_speech(self, text, userID):
        """
        Convert text to speech.
        :param text: Text to convert to audio
        :param userID: user in question
        :return: Audio data or file
        """
        # Add logic for text-to-speech conversion
        client = self.ELABSclient
        try:
            audio_stream = client.generate(text=text, voice='Brian', model="eleven_multilingual_v2")
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None
        
        output_dir = "../generated_audio"
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        file_path = os.path.join(output_dir, f'output_audio_{userID}_{timestamp}.mp3')

        try:
            # Write audio data to the file
            with open(file_path, "wb") as audio_file:
                for chunk in audio_stream:
                    audio_file.write(chunk)
            print(f"Audio saved to {file_path}")
            self.background_music(ad_file=file_path)
            return file_path
        except Exception as e:
            print(f"Error saving audio file: {e}")
            return None



    def background_music(self, ad_file, volume = 0.4):
        background_music = random.choice(self.musicList)
        output_file = f"../generated_audio/WithBackground{ad_file.split('/')[-1]}"
        try:
            (
                ffmpeg
                .filter(
                    [ffmpeg.input(ad_file), ffmpeg.input(background_music).filter('volume', volume)],
                    'amix', inputs=2, duration='shortest'
                )
                .output(output_file, acodec='mp3')  # Output as MP3
                .run(overwrite_output=True)
            )
            print(f"Success. Submitted to {output_file}")
            return output_file
        except ffmpeg.Error as e:
            print(f"Error occurred: {e.stderr.decode()}")
            return None

    def main(self):
        """
        Main method to execute the workflow.
        """
        user_id = random.randint(1, 99)
        device_type = random.choice(['mobile', 'tablet', 'desktop'])
        print(user_id, device_type)
        ad_rec = Similar_Users().recommend_ads(user_id, device_type)
        ad_response = self.automate_ad(ad_rec, user_id)
        print(ad_response)
        # self.text_to_speech(ad_response, user_id)


# Example usage
if __name__ == "__main__":
    ad_automation = AdAutomation()
    ad_automation.main()