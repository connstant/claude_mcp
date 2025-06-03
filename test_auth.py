#!/usr/bin/env python
"""
Test script for MCP Server authentication.
Tests both authenticated and unauthenticated requests to the health endpoint.
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:6921"
API_TOKEN = "ROCKY_MCP_TOKEN_2025"  # Using the same token as in Claude Desktop config

def test_health_check_no_auth():
    """Test the health endpoint without authentication."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check without auth: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_health_check_with_auth():
    """Test the health endpoint with authentication."""
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(f"{BASE_URL}/health", headers=headers)
        print(f"Health check with auth: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_mcp_endpoint_no_auth():
    """Test the MCP endpoint without authentication."""
    try:
        response = requests.post(f"{BASE_URL}/rpc", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "get_version"
        })
        print(f"MCP endpoint without auth: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code != 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_mcp_endpoint_with_auth():
    """Test the MCP endpoint with authentication."""
    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "get_version"
        }
        print(f"\nSending request to {BASE_URL}/rpc")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        
        response = requests.post(f"{BASE_URL}/rpc", json=payload, headers=headers)
        
        print(f"MCP endpoint with auth: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing MCP Server Authentication")
    print("=================================")
    
    # Make sure to update the API_TOKEN at the top of this script
    # to match the token in your environment or Claude Desktop config
    
    # Run tests
    health_no_auth = test_health_check_no_auth()
    health_with_auth = test_health_check_with_auth()
    mcp_no_auth = test_mcp_endpoint_no_auth()
    mcp_with_auth = test_mcp_endpoint_with_auth()
    
    # Print summary
    print("\nTest Results:")
    print(f"Health endpoint without auth: {'PASS' if health_no_auth else 'FAIL'}")
    print(f"Health endpoint with auth: {'PASS' if health_with_auth else 'FAIL'}")
    print(f"MCP endpoint without auth should fail: {'PASS' if mcp_no_auth else 'FAIL'}")
    print(f"MCP endpoint with auth: {'PASS' if mcp_with_auth else 'FAIL'}")
    
    # Check if all tests passed
    if health_no_auth and health_with_auth and mcp_no_auth and mcp_with_auth:
        print("\nAll tests passed! Your authentication is working correctly.")
        sys.exit(0)
    else:
        print("\nSome tests failed. Check your authentication configuration.")
        sys.exit(1)
