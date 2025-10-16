"""
Message Templates for Multi-Step Flow
Professional outreach templates for Instagram DM automation
"""

from database import AutomationDatabase

class MessageTemplates:
    """Pre-defined message templates for each step of the outreach flow"""
    
    # Step 1: Initial Outreach (Cold Outreach)
    STEP_1_TEMPLATES = [
        {
            "name": "Website Offer (Original)",
            "message": """Hey,
Love the cars in your line-up - awesome machines! 

A close friend told me about your rental company. 
I just checked your Instagram and, man, you're losing money without a site that generates you bookings.  

So, I created a live website w/ your cars for you. I can send you the link and, if you like it, we can work together. If no, no problem.

Reply "yes" to this message if you want to see your new luxurious website, tailored just to your rental company.""",
            "wait_days": 3
        },
        {
            "name": "Partnership Opportunity",
            "message": """Hi there! 👋

I came across your profile and I'm really impressed with what you're doing!

I work with businesses like yours to help them scale their online presence and increase revenue. 

I have a specific idea that could potentially double your reach in the next 30 days.

Would you be interested in a quick chat about it?""",
            "wait_days": 3
        },
        {
            "name": "Value-First Approach",
            "message": """Hey!

Just wanted to reach out because I noticed something about your business that caught my attention.

I analyzed your competitors and found 3 specific strategies they're using to get ahead. I'd love to share these insights with you - no strings attached!

Interested in hearing what I found?""",
            "wait_days": 3
        }
    ]
    
    # Step 2: First Follow-up (No response to initial message)
    STEP_2_TEMPLATES = [
        {
            "name": "Friendly Check-in",
            "message": """Hey again!

I know you're probably super busy running your business. 

Just wanted to check if you saw my previous message about the website I created for you?

I'm holding it for you for another 48 hours before I move on to other projects.

Let me know if you'd like to take a look - it only takes 2 minutes! 🚀""",
            "wait_days": 5
        },
        {
            "name": "Added Value Follow-up",
            "message": """Hi!

Quick follow-up to my last message...

I actually went ahead and did a bit more research on your business. I found 5 quick wins that could immediately improve your conversions.

Would you like me to send them over? It's completely free - just trying to provide value! 😊""",
            "wait_days": 5
        },
        {
            "name": "Urgency Follow-up",
            "message": """Hey there!

I hope I'm not bothering you, but I wanted to follow up one more time.

The offer I mentioned is actually time-sensitive - I can only work with 2 more clients this month.

If you're interested, just reply with "tell me more" and I'll send over the details.

If not, no worries at all! I'll stop reaching out. 🙏""",
            "wait_days": 5
        }
    ]
    
    # Step 3: Final Follow-up (Last attempt)
    STEP_3_TEMPLATES = [
        {
            "name": "Last Chance",
            "message": """Hi one last time!

I totally understand if this isn't the right time or if you're not interested.

Before I close your file, I wanted to give you one final opportunity to see what I've built for you.

Here's a quick preview: [Your business could be getting 10x more bookings]

If you want the full version, just say "yes". Otherwise, I wish you all the best with your business! 

This is my last message, promise! 🤝""",
            "wait_days": 7
        },
        {
            "name": "Break-up Message",
            "message": """Hey!

I haven't heard back from you, so I'm assuming you're either not interested or the timing isn't right.

No problem at all! I'll stop reaching out now.

If things change in the future and you'd like to explore working together, feel free to message me anytime.

Wishing you massive success! 💪""",
            "wait_days": 7
        },
        {
            "name": "Final Value Drop",
            "message": """Hi!

Since I haven't heard back, this will be my last message.

I don't want to leave without providing some value though! Here are 3 free resources that have helped similar businesses grow:

1. [Quick tip about your industry]
2. [Useful tool recommendation]
3. [Growth hack specific to your niche]

Hope these help! If you ever need anything, I'm just a message away.

Best of luck! 🌟""",
            "wait_days": 7
        }
    ]
    
    # Step 4: Re-engagement (After long pause - 30+ days)
    STEP_4_TEMPLATES = [
        {
            "name": "Re-engagement",
            "message": """Hey! It's been a while!

I wanted to reach back out because I just helped a business similar to yours achieve amazing results:

[Specific result/case study]

It reminded me of our previous conversation. 

Are you still looking to grow your business? The landscape has changed a lot and there are new opportunities available.

Would love to catch up if you're interested!""",
            "wait_days": 30
        }
    ]
    
    @classmethod
    def initialize_templates(cls, db: AutomationDatabase):
        """Initialize database with default templates if not exists"""
        existing_templates = db.get_all_templates()
        
        if not existing_templates:
            print("Initializing message templates...")
            
            # Add Step 1 templates
            for template in cls.STEP_1_TEMPLATES:
                db.add_message_template(
                    step_number=1,
                    template_name=f"Step 1: {template['name']}",
                    message_content=template['message'],
                    wait_days=template['wait_days']
                )
            
            # Add Step 2 templates
            for template in cls.STEP_2_TEMPLATES:
                db.add_message_template(
                    step_number=2,
                    template_name=f"Step 2: {template['name']}",
                    message_content=template['message'],
                    wait_days=template['wait_days']
                )
            
            # Add Step 3 templates
            for template in cls.STEP_3_TEMPLATES:
                db.add_message_template(
                    step_number=3,
                    template_name=f"Step 3: {template['name']}",
                    message_content=template['message'],
                    wait_days=template['wait_days']
                )
            
            # Add Step 4 templates
            for template in cls.STEP_4_TEMPLATES:
                db.add_message_template(
                    step_number=4,
                    template_name=f"Step 4: {template['name']}",
                    message_content=template['message'],
                    wait_days=template['wait_days']
                )
            
            print("✓ Message templates initialized successfully!")
            return True
        
        return False
    
    @classmethod
    def get_template_summary(cls):
        """Get a summary of available templates"""
        return {
            "Step 1 - Initial Outreach": len(cls.STEP_1_TEMPLATES),
            "Step 2 - First Follow-up": len(cls.STEP_2_TEMPLATES),
            "Step 3 - Final Follow-up": len(cls.STEP_3_TEMPLATES),
            "Step 4 - Re-engagement": len(cls.STEP_4_TEMPLATES)
        }
