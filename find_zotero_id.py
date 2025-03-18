#!/usr/bin/env python3
"""
Script to help find your Zotero user ID or group ID.

This script provides instructions on how to find your Zotero user ID or group ID,
which are required for the Zotero MCP server.
"""

import requests
import webbrowser
import sys

def main():
    """Provide instructions on how to find Zotero IDs."""
    print("Find Your Zotero IDs")
    print("====================")
    print("\nThis script will help you find your Zotero user ID or group ID.")
    
    print("\n1. Finding Your Zotero User ID")
    print("----------------------------")
    print("Your Zotero user ID is a numeric ID, not your username.")
    print("To find your user ID:")
    print("  a. Log in to https://www.zotero.org")
    print("  b. Go to https://www.zotero.org/settings/keys")
    print("  c. Look at the URL of your API key page")
    print("     It should be something like: https://www.zotero.org/settings/keys/USERID")
    print("     where USERID is your numeric user ID")
    
    # Ask if the user wants to open the Zotero settings page
    open_settings = input("\nWould you like to open the Zotero settings page now? (y/n): ")
    if open_settings.lower() == 'y':
        webbrowser.open("https://www.zotero.org/settings/keys")
        print("Browser opened to Zotero settings page.")
    
    print("\n2. Finding Your Zotero Group ID")
    print("-----------------------------")
    print("If you want to use a group library instead of your personal library:")
    print("  a. Go to your group page on Zotero")
    print("  b. Look at the URL, which should be: https://www.zotero.org/groups/GROUPID")
    print("     where GROUPID is your group ID")
    
    # Ask if the user wants to check their API key
    check_api_key = input("\nWould you like to check if your API key is valid? (y/n): ")
    if check_api_key.lower() == 'y':
        api_key = input("Enter your Zotero API key: ")
        user_id = input("Enter your Zotero user ID (numeric): ")
        
        # Check if the API key is valid
        try:
            response = requests.get(
                f"https://api.zotero.org/users/{user_id}/items",
                headers={"Zotero-API-Key": api_key},
                params={"limit": 1}
            )
            
            if response.status_code == 200:
                print("\nSuccess! Your API key and user ID are valid.")
                print(f"Found {len(response.json())} items in your library.")
            elif response.status_code == 403:
                print("\nError: Invalid API key or insufficient permissions.")
                print("Make sure your API key has read access to your library.")
            elif response.status_code == 400 and "Invalid user ID" in response.text:
                print("\nError: Invalid user ID.")
                print("Make sure you're using your numeric user ID, not your username.")
            else:
                print(f"\nError: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"\nError checking API key: {str(e)}")
    
    print("\n3. Updating Your .env File")
    print("------------------------")
    print("Once you have your IDs, update the .env file in the zotero-mcp-server directory:")
    print("  ZOTERO_API_KEY=your_api_key_here")
    print("  ZOTERO_USER_ID=your_numeric_user_id_here")
    print("  # ZOTERO_GROUP_ID=your_group_id_here  # Uncomment to use a group library")
    
    print("\nFor more information, see the Zotero API documentation:")
    print("https://www.zotero.org/support/dev/web_api/v3/basics")

