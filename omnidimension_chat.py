import os
import json
from omnidimension import Client

class BoliBazaarChatSystem:
    def __init__(self):
        self.api_key = "P-rBV6jy7fmjIzrFHzMcx_IuWq0cVZsm5NV-CRCfews"
        self.client = Client(self.api_key)
        self.agent_id = None
        
    def setup_bolibazaar_agent(self):
        """Create BoliBazaar chat agent"""
        try:
            response = self.client.agent.create(
                name="BoliBazaar Assistant",
                welcome_message="Welcome to BoliBazaar! I'm your bidding assistant. Please provide your 6-digit unique ID to get started.",
                context_breakdown=[
                    {
                        "title": "Purpose", 
                        "body": "I help users with their auction bidding activities on BoliBazaar platform including checking bids, placing new bids, and getting auction information."
                    },
                    {
                        "title": "Authentication", 
                        "body": "Always ask for the user's 6-digit unique ID first. Verify it before providing any bidding services."
                    },
                    {
                        "title": "Services", 
                        "body": "I can help with: checking active bids, viewing auction details, placing new bids, checking bid history, and getting real-time auction status."
                    },
                    {
                        "title": "Communication Style", 
                        "body": "Be friendly, helpful, and professional. Use clear formatting for bid information and always confirm before placing bids."
                    }
                ],
                call_type="Incoming",
                model={
                    "model": "gpt-4o-mini",
                    "temperature": 0.3
                },
                web_search={"enabled": False},
                post_call_actions={
                    "extracted_variables": [
                        {
                            "key": "user_id",
                            "prompt": "Extract the 6-digit unique user ID provided by the user"
                        },
                        {
                            "key": "action_requested",
                            "prompt": "What action did the user request? (check_bids, place_bid, auction_details, bid_history, auction_status)"
                        },
                        {
                            "key": "bid_amount",
                            "prompt": "If placing a bid, what amount did they specify?"
                        },
                        {
                            "key": "auction_id",
                            "prompt": "Which auction ID did they mention?"
                        }
                    ]
                }
            )
            
            self.agent_id = response.get('id')
            print(f"BoliBazaar agent created: {self.agent_id}")
            return response
            
        except Exception as e:
            print(f"Error creating agent: {e}")
            return None

    def create_api_integrations(self):
        """Create API integrations with BoliBazaar"""
        try:
            base_url = "https://bolibazaar.onrender.com"
            
            integrations = {}
            
            # User verification
            integrations['verify_user'] = self.client.integrations.create_custom_api_integration(
                name="Verify User",
                description="Verify user by unique ID",
                url=f"{base_url}/api/users/verify/",
                method="POST",
                headers=[{"key": "Content-Type", "value": "application/json"}],
                body_type="json",
                body_params=[{
                    "key": "user_id",
                    "description": "6-digit unique user ID",
                    "type": "string",
                    "required": True,
                    "isLLMGenerated": False
                }]
            )
            
            # Get active bids
            integrations['active_bids'] = self.client.integrations.create_custom_api_integration(
                name="Get Active Bids",
                description="Get user's active bids",
                url=f"{base_url}/api/bids/active/",
                method="GET",
                headers=[{"key": "Content-Type", "value": "application/json"}],
                query_params=[{
                    "key": "user_id",
                    "description": "6-digit unique user ID",
                    "type": "string",
                    "required": True,
                    "isLLMGenerated": False
                }]
            )
            
            # Place bid
            integrations['place_bid'] = self.client.integrations.create_custom_api_integration(
                name="Place Bid",
                description="Place a new bid",
                url=f"{base_url}/api/bids/place/",
                method="POST",
                headers=[{"key": "Content-Type", "value": "application/json"}],
                body_type="json",
                body_params=[
                    {
                        "key": "user_id",
                        "description": "6-digit unique user ID",
                        "type": "string",
                        "required": True,
                        "isLLMGenerated": False
                    },
                    {
                        "key": "auction_id",
                        "description": "Auction ID",
                        "type": "string",
                        "required": True,
                        "isLLMGenerated": False
                    },
                    {
                        "key": "bid_amount",
                        "description": "Bid amount",
                        "type": "number",
                        "required": True,
                        "isLLMGenerated": False
                    }
                ]
            )
            
            # Get auction details
            integrations['auction_details'] = self.client.integrations.create_custom_api_integration(
                name="Get Auction Details",
                description="Get detailed auction information",
                url=f"{base_url}/api/auctions/details/",
                method="GET",
                headers=[{"key": "Content-Type", "value": "application/json"}],
                query_params=[{
                    "key": "auction_id",
                    "description": "Auction ID",
                    "type": "string",
                    "required": True,
                    "isLLMGenerated": False
                }]
            )
            
            return integrations
            
        except Exception as e:
            print(f"Error creating integrations: {e}")
            return {}

    def attach_integrations(self, integrations):
        """Attach integrations to agent"""
        try:
            for name, integration in integrations.items():
                if integration and 'id' in integration:
                    self.client.integrations.add_integration_to_agent(
                        self.agent_id, 
                        integration['id']
                    )
                    print(f"Attached {name} integration")
            return True
        except Exception as e:
            print(f"Error attaching integrations: {e}")
            return False

def setup_bolibazaar_chat():
    """Setup the complete BoliBazaar chat system"""
    chat_system = BoliBazaarChatSystem()
    
    # Create agent
    agent = chat_system.setup_bolibazaar_agent()
    if not agent:
        return None
    
    # Create integrations
    integrations = chat_system.create_api_integrations()
    if integrations:
        chat_system.attach_integrations(integrations)
    
    return chat_system

if __name__ == "__main__":
    setup_bolibazaar_chat()