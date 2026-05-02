import instaloader
from typing import List, Dict, Any
from utils.logger import logger
from services.rate_limiter import ig_limiter

class ViralEngine:
    def __init__(self, L: instaloader.Instaloader):
        self.L = L

    def get_top_viral_posts(self, username: str, limit: int = 15, analyze_last: int = 50) -> List[Dict[str, Any]]:
        """
        Analyzes the last `analyze_last` posts of a user.
        Calculates engagement rate: (likes + comments) / followers.
        Returns the top `limit` most viral videos.
        """
        ig_limiter.wait()
        logger.info(f"[ViralEngine] Analyzing profile: {username}")
        
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
            followers = profile.followers
            if followers == 0:
                followers = 1  # prevent div by zero
                
            posts = profile.get_posts()
            
            scored_posts = []
            count = 0
            
            for post in posts:
                if count >= analyze_last:
                    break
                    
                if post.is_video:
                    likes = post.likes
                    comments = post.comments
                    engagement = (likes + comments) / followers
                    
                    # Optional: apply time decay here based on post.date_utc if needed
                    
                    scored_posts.append({
                        "shortcode": post.shortcode,
                        "engagement_rate": engagement,
                        "likes": likes,
                        "comments": comments,
                        "date": post.date_utc
                    })
                count += 1
                
                # Small sleep to avoid instant block when iterating many posts
                if count % 10 == 0:
                    ig_limiter.wait()

            # Sort by engagement_rate descending
            scored_posts.sort(key=lambda x: x["engagement_rate"], reverse=True)
            top_viral = scored_posts[:limit]
            
            logger.info(f"[ViralEngine] Found {len(top_viral)} highly engaging videos for {username}.")
            return top_viral
            
        except Exception as e:
            logger.error(f"[ViralEngine] Analysis failed for {username}: {e}")
            raise
