# algomojo_webhook_signal/signal.py

import requests
import json 

def place_strategy_signal(webhook_url: str, date: str, action: str) -> str:
    """
    Function to place a strategy signal via Algomojo webhook.

    :param webhook_url: The webhook URL obtained from the Algomojo strategy screen.
    :param date: The order execution date and time (format: YYYY-MM-DD HH:MM:SS).
    :param action: "BUY" or "SELL" to define the order direction.
    :return: Response message indicating success or failure.
    """
    try:
        payload = {"date": date, "action": action}
        headers = {"Content-Type": "application/json"}

        response = requests.post(webhook_url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code == 200 and response_data.get("status") == "success":
            return f"Signal placed successfully: {response_data}"
        else:
            return f"Error placing signal: {response_data.get('error_msg', 'Unknown error')}"

    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"
    except json.JSONDecodeError:
        return "Error decoding response JSON"
    except Exception as e:
        return f"Unexpected error: {e}"
