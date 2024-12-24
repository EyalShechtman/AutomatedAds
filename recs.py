from collections import defaultdict
import pandas as pd
import json

class Similar_Users:
    def recommend_ads(self, user_id, device_type):
        """
        UserId: Int
        device_Type: String ('mobile', 'desktop', 'tablet')
        Returns: List [top 5 ads]

        Tries to "recreate" spotify ad picking algo in a very simple way.
        Recieve the User needed to provide an ad for and the device its from; 
        returns list of top 5 potential ads that would be appropriate for the user

        """
        ads_df = pd.read_csv('./synthetic-browsing-history/ads_df.csv')
        events_df = pd.read_csv('./synthetic-browsing-history/events_df.csv')
        # Filter user-specific events
        user_events = events_df[events_df["User_id"] == user_id]

        # Extract preferences
        preferred_categories = user_events["product_category"].value_counts().index.tolist()
        preferred_companies = user_events["product_name"].value_counts().index.tolist()
        preferred_device = user_events["device_type"].value_counts().idxmax()

        # Ads already seen by the user
        seen_ads = user_events["ad_id"].dropna().unique()

        # Filter ads not yet seen
        ads_candidates = ads_df[
            ~ads_df["Ad_id"].isin(seen_ads) &  # Exclude seen ads
            ads_df["AdCategory"].isin(preferred_categories)  # Match preferred categories
        ].copy()  # Ensure a deep copy to avoid warnings

        # Score ads based on relevance
        ads_candidates.loc[:, "score"] = ads_candidates["AdCategory"].apply(
            lambda cat: preferred_categories.index(cat) + 1 if cat in preferred_categories else 0
        )
        ads_candidates = ads_candidates.sort_values("score", ascending=False)

        ads_candidates.loc[:, "company_match"] = ads_candidates["AdText"].apply(
            lambda text: any(company in text for company in preferred_companies)
        )
        ads_candidates.loc[:, "score"] += ads_candidates["company_match"] * 1.2

        ads_candidates.loc[:, "device_match"] = ads_candidates["Ad_id"].apply(
            lambda ad: device_type == preferred_device
        )
        ads_candidates.loc[:, "score"] += ads_candidates["device_match"] * 1.2

        ads_candidates = ads_candidates.sort_values("score", ascending=False)
        top_ads = ads_candidates.head(5)

        return top_ads[["AdText", 'AdCategory']].to_json(orient='records')

# similarUsers = Similar_Users()
# similarUsers.recommend_ads(2, 'mobile')