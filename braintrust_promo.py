import praw
import time
import random
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='braintrust_bot.log'
)

class BraintrustPromoBot:
    def __init__(self):
        # Initialize Reddit instance
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT'),
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD'),
        )
        # Verify Reddit instance
        print(self.reddit.user.me())
        try:
            # This will raise an exception if authentication fails
            self.reddit.user.me()
            print("Successfully authenticated with Reddit")
        except Exception as e:
            print(f"Failed to authenticate: {str(e)}")
            raise

        
        # Your Braintrust referral link
        self.referral_link = os.getenv('REFERRAL_LINK')
        
        # Expanded list of target subreddits with categories
        self.target_subreddits = {
            'freelance_general': [
                'freelance', 'freelancewriters', 'freelancers', 'digitalnomad',
                'WorkOnline', 'forhire', 'freelance_forhire', 'hireawriter'
            ],
            'tech_specific': [
                'webdev', 'programming', 'developers', 'softwaredevelopment',
                'javascript', 'python', 'coding', 'learningprogramming',
                'cscareerquestions', 'devops', 'fullstack'
            ],
            'design': [
                'UI_Design', 'UXDesign', 'graphic_design', 'web_design',
                'userexperience', 'Design'
            ],
            'career_development': [
                'careerguidance', 'careerchange', 'jobs', 'remotework',
                'WorkRemote', 'sidehustle'
            ]
        }
        
        # Keywords to monitor for potential comment opportunities
        self.keywords = [
            'freelance platform', 'upwork', 'fiverr', 'freelancer', 'remote work',
            'self employed', 'side gig', 'programming job', 'developer job',
            'looking for work', 'hiring developers', 'tech job', 'contract work'
        ]
        
        # Enhanced message templates targeting different freelancer segments
        self.message_templates = [
            {
                'category': 'tech',
                'title': "Tech Freelancers: Why I Switched to Braintrust (0% Fees + Token Ownership)",
                'content': """Fellow tech freelancers! 

After years on traditional platforms, I discovered Braintrust and here's what makes it unique for tech professionals:

Recent Client Examples:
- Fortune 500 tech companies
- Funded startups
- Enterprise software projects

Financial Benefits:
• 0% platform fees (vs 20% on other platforms)
• Higher average hourly rates ($80-200+/hour)
• Get paid in USD, plus earn BTRST tokens

Key Advantages:
• Direct client relationships
• Network ownership through BTRST
• Professional vetting process
• Enterprise-level projects
• Long-term contracts available

For junior and senior developers, architects, and tech leads interested in joining: {referral_link}

Feel free to ask any questions about the platform or my experience!"""
            },
            {
                'category': 'design',
                'title': "Designers: Premium Freelance Platform with 0% Fees (Braintrust Review)",
                'content': """Hey fellow designers! 🎨

If you're tired of high platform fees eating into your earnings, check out Braintrust:

Design Opportunities:
• UI/UX Design
• Product Design
• Brand Identity
• Design Systems
• User Research

Platform Benefits:
• Keep 100% of your earnings
• Work with top-tier clients
• Earn ownership (BTRST tokens)
• Professional community

Ready to upgrade your freelance game? Join here: {referral_link}

Would love to connect with other designers on the platform!"""
            },
            {
                'category': 'general',
                'title': "Freelancers: How I'm Making More While Paying 0% Fees (Braintrust Platform)",
                'content': """Hey freelance community!

Wanted to share a platform that's genuinely different from the usual suspects:

Why Braintrust Stands Out:
• 0% commission (you keep everything you earn)
• Ownership in the platform through BTRST tokens
• Enterprise clients with serious budgets
• Professional, vetted talent pool

Best For:
• Experienced professionals
• Tech & creative experts
• Long-term contract seekers
• Quality-focused freelancers

Current opportunities in:
✅ Development
✅ Design
✅ Product Management
✅ Data Science
✅ DevOps
✅ Technical Writing

Join using my referral link: {referral_link}

Let me know if you have any questions about getting started!"""
            }
        ]

    def monitor_keywords(self):
        """Monitor subreddits for keyword mentions and respond appropriately"""
        subreddits = '+'.join([sub for sublist in self.target_subreddits.values() for sub in sublist])
        subreddit = self.reddit.subreddit(subreddits)
        
        for comment in subreddit.comments(limit=100):
            # Check if we've already replied
            if self.has_replied(comment):
                continue
                
            # Look for relevant keywords in comments
            if any(keyword.lower() in comment.body.lower() for keyword in self.keywords):
                self.respond_to_comment(comment)
                
    def has_replied(self, comment):
        """Check if we've already replied to this comment"""
        comment.refresh()
        for reply in comment.replies:
            if reply.author is not None and reply.author.name == self.reddit.user.me().name:
                return True
        return False

    def check_post_exists(self, subreddit_name):
        """Check if we've already posted in the subreddit within the last 24 hours"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            # Get the bot's username
            username = self.reddit.user.me().name
            
            # Check recent posts in the subreddit
            for post in subreddit.new(limit=25):  # Check last 25 posts
                if post.author and post.author.name == username:
                    # Check if post is less than 24 hours old
                    post_time = datetime.fromtimestamp(post.created_utc)
                    time_difference = datetime.now() - post_time
                    
                    if time_difference.total_seconds() < 86400:  # 24 hours in seconds
                        return True
                        
            return False
            
        except Exception as e:
            logging.error(f"Error checking existing posts in r/{subreddit_name}: {str(e)}")
            return True  # Return True on error to prevent posting

    def respond_to_comment(self, comment):
        """Respond to relevant comments with appropriate information"""
        try:
            # Customize response based on context
            if any(word in comment.body.lower() for word in ['upwork', 'fiverr', 'fees']):
                response = """Hey! If you're looking for a platform with 0% fees, you might want to check out Braintrust. Unlike traditional platforms, you keep 100% of what you earn plus earn ownership tokens. Here's my referral link if you're interested: {}""".format(self.referral_link)
            elif any(word in comment.body.lower() for word in ['looking for work', 'hiring']):
                response = """If you're looking for quality tech/creative opportunities, Braintrust connects freelancers with Fortune 500 companies and funded startups. They have 0% fees and you earn ownership tokens. Here's more info: {}""".format(self.referral_link)
            else:
                return

            comment.reply(response)
            logging.info(f"Replied to comment: {comment.id}")
            print(f"Replied to comment: {comment.id}")
            time.sleep(random.randint(300, 600))  # Wait 5-10 minutes between comments
            
        except Exception as e:
            logging.error(f"Error responding to comment {comment.id}: {str(e)}")

    def create_post(self, subreddit_name):
        """Create a new post in the specified subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Check if we've posted recently
            if self.check_post_exists(subreddit_name):
                logging.info(f"Already posted in r/{subreddit_name} today. Skipping.")
                return
            
            # Choose appropriate template based on subreddit category
            category = next((cat for cat, subs in self.target_subreddits.items() 
                           if subreddit_name in subs), 'general')
            
            suitable_templates = [t for t in self.message_templates 
                                if t['category'] == category or t['category'] == 'general']
            template = random.choice(suitable_templates)
            
            # Create post
            post = subreddit.submit(
                title=template['title'],
                selftext=template['content'].format(referral_link=self.referral_link)
            )
            
            logging.info(f"Successfully posted to r/{subreddit_name}: {post.url}")
            print(f"Successfully posted to r/{subreddit_name}: {post.url}")

            # Wait to avoid rate limiting
            time.sleep(random.randint(600, 1200))  # Wait 10-20 minutes between posts
            
        except Exception as e:
            logging.error(f"Error posting to r/{subreddit_name}: {str(e)}")

    def run(self):
        """Main function to run the bot"""
        logging.info("Starting Braintrust promotion bot")
        
        while True:
            # Post in each subreddit category
            '''for category, subreddits in self.target_subreddits.items():
                for subreddit in subreddits:
                    self.create_post(subreddit)'''
            
            # Monitor for keywords and respond to relevant comments
            self.monitor_keywords()
            
            # Wait before next cycle
            logging.info("Completed posting cycle. Waiting 24 hours...")
            time.sleep(86400)  # Wait 24 hours

def main():
    bot = BraintrustPromoBot()
    bot.run()

if __name__ == "__main__":
    main()