import requests

class BulkSMSSender:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url

    def send_sms(self, phone_numbers, message):
        """Send SMS to a list of phone numbers."""
        for phone_number in phone_numbers:
            payload = {
                'api_key': self.api_key,
                'to': phone_number,
                'message': message
            }

            response = requests.post(self.api_url, data=payload)

            if response.status_code == 200:
                print(f"Message sent to {phone_number}")
            else:
                print(f"Failed to send message to {phone_number}")

# Usage example
if __name__ == "__main__":
    # Replace with your actual API details
    api_key = "your_api_key"
    api_url = "https://api.smslocal.com/send"
    
    sms_sender = BulkSMSSender(api_key, api_url)
    
    phone_numbers = ["+1234567890", "+0987654321"]
    message = "Hello, this is a bulk SMS test."
    
    sms_sender.send_sms(phone_numbers, message)
