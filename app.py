from flask import Flask, request, jsonify
import json
import requests
from typing import Dict, List, Any, Optional
import os
from datetime import datetime

app = Flask(__name__)

class SmartHospitalAgent:
    def __init__(self, openrouter_api_key: str, hospital_base_url: str = "https://dt-agent-api.onrender.com/", use_function_calling: bool = False):
        self.openrouter_api_key = openrouter_api_key
        self.hospital_base_url = hospital_base_url
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "tngtech/deepseek-r1t2-chimera:free"
        self.use_function_calling = use_function_calling
        
        # Define available hospital tools
        self.tools = self._define_hospital_tools()
    
    def _define_hospital_tools(self) -> List[Dict]:
        """Define all available hospital API tools for the AI agent"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_all_patients",
                    "description": "Get all patients with optional filtering by ward, status, or risk level",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ward": {"type": "string", "description": "Filter by ward (e.g., 'Cardiology')"},
                            "status": {"type": "string", "description": "Filter by current status (stable, critical, improving, deteriorating)"},
                            "risk_level": {"type": "string", "description": "Filter by risk level (Low, Moderate, High, Critical)"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_patient",
                    "description": "Get a specific patient's complete record",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "string", "description": "The patient ID"}
                        },
                        "required": ["patient_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_patient",
                    "description": "Create a new patient record",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_data": {"type": "object", "description": "Patient data object"}
                        },
                        "required": ["patient_data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_patient",
                    "description": "Update a patient's complete record",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "string", "description": "The patient ID"},
                            "patient_data": {"type": "object", "description": "Updated patient data"}
                        },
                        "required": ["patient_id", "patient_data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_patient_vitals",
                    "description": "Get patient's vital signs history",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "string", "description": "The patient ID"},
                            "start_time": {"type": "string", "description": "Start time filter"},
                            "end_time": {"type": "string", "description": "End time filter"},
                            "limit": {"type": "integer", "description": "Limit number of results", "default": 10}
                        },
                        "required": ["patient_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_patient_treatments",
                    "description": "Get patient's treatment history",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "string", "description": "The patient ID"},
                            "status": {"type": "string", "description": "Filter by treatment status"}
                        },
                        "required": ["patient_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "predict_patient_risk",
                    "description": "Predict risk level for a patient",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "string", "description": "The patient ID"}
                        },
                        "required": ["patient_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_alerts",
                    "description": "Get current active alerts",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_staff",
                    "description": "List all staff members with optional filters",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string", "description": "Filter by staff role"},
                            "department": {"type": "string", "description": "Filter by department"},
                            "onDuty": {"type": "boolean", "description": "Filter by duty status"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_staff",
                    "description": "Get staff member details by ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "staff_id": {"type": "string", "description": "The staff ID"}
                        },
                        "required": ["staff_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_staff_schedule",
                    "description": "Get staff schedule for a date range",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "staff_id": {"type": "string", "description": "The staff ID"},
                            "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                            "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"}
                        },
                        "required": ["staff_id", "start_date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_iot_devices",
                    "description": "Get all IoT devices and their vitals",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_device_data",
                    "description": "Get all sensor data for a specific device",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {"type": "string", "description": "The device ID"}
                        },
                        "required": ["device_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_latest_vitals",
                    "description": "Get the most recent vitals reading for current patient on a device",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {"type": "string", "description": "The device ID"}
                        },
                        "required": ["device_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "detect_anomaly",
                    "description": "Detect anomalies for a specific monitor",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "monitor_id": {"type": "string", "description": "The monitor ID"}
                        },
                        "required": ["monitor_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_anomalies",
                    "description": "Get all anomalies across all devices",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "hours": {"type": "integer", "description": "Hours to look back", "default": 24},
                            "severity_filter": {"type": "string", "description": "Filter by severity"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_rooms",
                    "description": "Get all rooms",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_room",
                    "description": "Get a specific room by ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "room_id": {"type": "string", "description": "The room ID"}
                        },
                        "required": ["room_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assign_patient_to_room",
                    "description": "Assign a patient to a room",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "room_id": {"type": "string", "description": "The room ID"},
                            "patient_id": {"type": "string", "description": "The patient ID"}
                        },
                        "required": ["room_id", "patient_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_beds",
                    "description": "Get all beds",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_bed",
                    "description": "Get a specific bed by ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "bed_id": {"type": "string", "description": "The bed ID"}
                        },
                        "required": ["bed_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assign_patient_to_bed",
                    "description": "Assign a patient to a specific bed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "bed_id": {"type": "string", "description": "The bed ID"},
                            "patient_id": {"type": "string", "description": "The patient ID"}
                        },
                        "required": ["bed_id", "patient_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_simulation_status",
                    "description": "Get the current status of the data simulation",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
    
    def _make_hospital_api_call(self, endpoint: str, method: str = "GET", data: Dict = None, params: Dict = None) -> Dict:
        """Make API call to the hospital backend"""
        url = f"{self.hospital_base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, json=data, params=params)
            elif method == "PUT":
                response = requests.put(url, json=data, params=params)
            elif method == "PATCH":
                response = requests.patch(url, json=data, params=params)
            elif method == "DELETE":
                response = requests.delete(url, params=params)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API call failed: {str(e)}"}
    
    def _execute_hospital_function(self, function_name: str, arguments: Dict) -> Dict:
        """Execute a hospital API function based on the function name and arguments"""
        
        # Patient endpoints
        if function_name == "get_all_patients":
            return self._make_hospital_api_call("/patients/", params=arguments)
        
        elif function_name == "get_patient":
            patient_id = arguments.get("patient_id")
            return self._make_hospital_api_call(f"/patients/{patient_id}")
        
        elif function_name == "create_patient":
            patient_data = arguments.get("patient_data")
            return self._make_hospital_api_call("/patients/", method="POST", data=patient_data)
        
        elif function_name == "update_patient":
            patient_id = arguments.get("patient_id")
            patient_data = arguments.get("patient_data")
            return self._make_hospital_api_call(f"/patients/{patient_id}", method="PUT", data=patient_data)
        
        elif function_name == "get_patient_vitals":
            patient_id = arguments.get("patient_id")
            params = {k: v for k, v in arguments.items() if k != "patient_id" and v is not None}
            return self._make_hospital_api_call(f"/patients/{patient_id}/vitals", params=params)
        
        elif function_name == "get_patient_treatments":
            patient_id = arguments.get("patient_id")
            params = {k: v for k, v in arguments.items() if k != "patient_id" and v is not None}
            return self._make_hospital_api_call(f"/patients/{patient_id}/treatments", params=params)
        
        elif function_name == "predict_patient_risk":
            patient_id = arguments.get("patient_id")
            return self._make_hospital_api_call(f"/predict/risk/{patient_id}")
        
        # Alert endpoints
        elif function_name == "get_current_alerts":
            return self._make_hospital_api_call("/alerts/")
        
        # Staff endpoints
        elif function_name == "get_all_staff":
            return self._make_hospital_api_call("/staff/", params=arguments)
        
        elif function_name == "get_staff":
            staff_id = arguments.get("staff_id")
            return self._make_hospital_api_call(f"/staff/{staff_id}")
        
        elif function_name == "get_staff_schedule":
            staff_id = arguments.get("staff_id")
            params = {k: v for k, v in arguments.items() if k != "staff_id" and v is not None}
            return self._make_hospital_api_call(f"/staff/{staff_id}/schedule", params=params)
        
        # IoT Device endpoints
        elif function_name == "get_all_iot_devices":
            return self._make_hospital_api_call("/iotData/")
        
        elif function_name == "get_device_data":
            device_id = arguments.get("device_id")
            return self._make_hospital_api_call(f"/iotData/{device_id}")
        
        elif function_name == "get_latest_vitals":
            device_id = arguments.get("device_id")
            return self._make_hospital_api_call(f"/iotData/{device_id}/vitals/latest")
        
        # Anomaly Detection endpoints
        elif function_name == "detect_anomaly":
            monitor_id = arguments.get("monitor_id")
            return self._make_hospital_api_call(f"/anomalies/detect/{monitor_id}")
        
        elif function_name == "get_all_anomalies":
            return self._make_hospital_api_call("/anomalies/", params=arguments)
        
        # Room endpoints
        elif function_name == "get_all_rooms":
            return self._make_hospital_api_call("/rooms/")
        
        elif function_name == "get_room":
            room_id = arguments.get("room_id")
            return self._make_hospital_api_call(f"/rooms/{room_id}")
        
        elif function_name == "assign_patient_to_room":
            room_id = arguments.get("room_id")
            patient_id = arguments.get("patient_id")
            return self._make_hospital_api_call(f"/rooms/{room_id}/assign-patient/{patient_id}", method="POST")
        
        # Bed endpoints
        elif function_name == "get_all_beds":
            return self._make_hospital_api_call("/beds/")
        
        elif function_name == "get_bed":
            bed_id = arguments.get("bed_id")
            return self._make_hospital_api_call(f"/beds/{bed_id}")
        
        elif function_name == "assign_patient_to_bed":
            bed_id = arguments.get("bed_id")
            patient_id = arguments.get("patient_id")
            return self._make_hospital_api_call(f"/beds/{bed_id}/assign-patient/{patient_id}", method="POST")
        
        # Simulation endpoints
        elif function_name == "get_simulation_status":
            return self._make_hospital_api_call("/simulation/status")
        
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    def chat_with_tools(self, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """Send a message to the AI with access to hospital tools"""
        
        if conversation_history is None:
            conversation_history = []
        
        # Check if the user message requires hospital data
        hospital_keywords = [
            'patient', 'staff', 'room', 'bed', 'alert', 'vital', 'device', 
            'iot', 'anomaly', 'treatment', 'schedule', 'simulation', 'ward',
            'critical', 'monitor', 'hospital'
        ]
        
        needs_hospital_data = any(keyword in user_message.lower() for keyword in hospital_keywords)
        
        if needs_hospital_data and not self.use_function_calling:
            # Try to determine what data is needed and fetch it
            hospital_data = self._get_relevant_hospital_data(user_message)
            
            # Add system message with hospital data context
            system_message = f"""You are an AI assistant for a Smart Hospital Management System. 

Based on the user's question, here is the relevant hospital data:

{json.dumps(hospital_data, indent=2)}

Use this data to answer the user's question. Be professional and prioritize patient safety and privacy."""
        else:
            # Standard system message
            system_message = """You are an AI assistant for a Smart Hospital Management System. You have access to various hospital tools and APIs that allow you to:

- Manage patient records, vitals, and treatments
- Monitor staff schedules and assignments
- Track IoT devices and sensor data
- Detect anomalies in patient monitoring
- Manage room and bed assignments
- View alerts and simulation status

When users ask questions about the hospital, use the appropriate tools to gather information and provide helpful responses. Always be professional and prioritize patient safety and privacy."""
        
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Prepare the request payload
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        # Only add tools if function calling is enabled
        if self.use_function_calling:
            payload["tools"] = self.tools
            payload["tool_choice"] = "auto"
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/smart-hospital-system",
            "X-Title": "Smart Hospital AI Agent"
        }
        
        try:
            # Debug: Print the API key (first and last 10 characters only for security)
            api_key_debug = f"{self.openrouter_api_key[:10]}...{self.openrouter_api_key[-10:]}" if len(self.openrouter_api_key) > 20 else "KEY_TOO_SHORT"
            print(f"DEBUG: Using API key: {api_key_debug}")
            print(f"DEBUG: Full headers: {headers}")
            
            # Make the API call to OpenRouter
            response = requests.post(self.openrouter_url, data=json.dumps(payload), headers=headers)
            
            # Debug: Print response details
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response headers: {response.headers}")
            
            response.raise_for_status()
            response_data = response.json()
            
            message = response_data["choices"][0]["message"]
            
            # Check if the AI wants to use tools (only if function calling is enabled)
            if self.use_function_calling and message.get("tool_calls"):
                # Execute each tool call
                tool_results = []
                
                for tool_call in message["tool_calls"]:
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])
                    
                    # Execute the hospital function
                    result = self._execute_hospital_function(function_name, function_args)
                    
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "content": json.dumps(result)
                    })
                
                # Add the assistant's message and tool results to conversation
                messages.append(message)
                messages.extend(tool_results)
                
                # Make another API call to get the final response
                payload["messages"] = messages
                final_response = requests.post(self.openrouter_url, data=json.dumps(payload), headers=headers)
                final_response.raise_for_status()
                final_data = final_response.json()
                
                return {
                    "response": final_data["choices"][0]["message"]["content"],
                    "tool_calls_made": len(tool_results),
                    "tools_used": [tc["function"]["name"] for tc in message["tool_calls"]],
                    "conversation_history": messages
                }
            else:
                return {
                    "response": message["content"],
                    "tool_calls_made": 0,
                    "tools_used": [],
                    "conversation_history": messages
                }
                
        except requests.exceptions.RequestException as e:
            # More detailed error information
            error_details = f"OpenRouter API call failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_json = e.response.json()
                    error_details += f" - Response: {error_json}"
                except:
                    error_details += f" - Response text: {e.response.text}"
            return {"error": error_details}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def _get_relevant_hospital_data(self, user_message: str) -> Dict:
        """Fetch relevant hospital data based on the user's message"""
        data = {}
        message_lower = user_message.lower()
        
        try:
            # Get patients if mentioned
            if any(word in message_lower for word in ['patient', 'patients']):
                patients = self._make_hospital_api_call("/patients/")
                data['patients'] = patients
            
            # Get alerts if mentioned
            if any(word in message_lower for word in ['alert', 'alerts']):
                alerts = self._make_hospital_api_call("/alerts/")
                data['alerts'] = alerts
            
            # Get staff if mentioned
            if any(word in message_lower for word in ['staff', 'doctor', 'nurse']):
                staff = self._make_hospital_api_call("/staff/")
                data['staff'] = staff
            
            # Get rooms if mentioned
            if any(word in message_lower for word in ['room', 'rooms']):
                rooms = self._make_hospital_api_call("/rooms/")
                data['rooms'] = rooms
            
            # Get beds if mentioned
            if any(word in message_lower for word in ['bed', 'beds']):
                beds = self._make_hospital_api_call("/beds/")
                data['beds'] = beds
            
            # Get IoT devices if mentioned
            if any(word in message_lower for word in ['device', 'devices', 'iot', 'sensor']):
                devices = self._make_hospital_api_call("/iotData/")
                data['iot_devices'] = devices
            
            # Get anomalies if mentioned
            if any(word in message_lower for word in ['anomaly', 'anomalies']):
                anomalies = self._make_hospital_api_call("/anomalies/")
                data['anomalies'] = anomalies
            
            # Get simulation status if mentioned
            if any(word in message_lower for word in ['simulation', 'status']):
                simulation = self._make_hospital_api_call("/simulation/status")
                data['simulation_status'] = simulation
                
        except Exception as e:
            data['error'] = f"Error fetching hospital data: {str(e)}"
        
        return data

# Initialize the agent
agent = None

def get_agent():
    global agent
    if agent is None:
        # Try to get API key from environment variable first, then fallback to hardcoded
        api_key = os.environ.get('OPENROUTER_API_KEY', "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")
        
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        print(f"DEBUG: Initializing agent with API key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else 'TOO_SHORT'}")
        agent = SmartHospitalAgent(api_key, use_function_calling=False)
    return agent

# Flask API endpoints
@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Smart Hospital AI Agent API is running",
        "version": "1.0.0"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' in request body"
            }), 400
        
        user_message = data['message']
        conversation_history = data.get('conversation_history', [])
        
        # Get agent and process message
        hospital_agent = get_agent()
        result = hospital_agent.chat_with_tools(user_message, conversation_history)
        
        if "error" in result:
            return jsonify({
                "error": result["error"]
            }), 500
        
        return jsonify({
            "response": result["response"],
            "tool_calls_made": result.get("tool_calls_made", 0),
            "tools_used": result.get("tools_used", []),
            "conversation_history": result.get("conversation_history", [])
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/hospital-data/<endpoint>', methods=['GET'])
def get_hospital_data(endpoint):
    """Direct access to hospital data endpoints"""
    try:
        hospital_agent = get_agent()
        
        # Map endpoint to hospital API call
        endpoint_map = {
            'patients': '/patients/',
            'alerts': '/alerts/',
            'staff': '/staff/',
            'rooms': '/rooms/',
            'beds': '/beds/',
            'devices': '/iotData/',
            'anomalies': '/anomalies/',
            'simulation': '/simulation/status'
        }
        
        if endpoint not in endpoint_map:
            return jsonify({
                "error": f"Unknown endpoint: {endpoint}"
            }), 400
        
        result = hospital_agent._make_hospital_api_call(endpoint_map[endpoint])
        
        if "error" in result:
            return jsonify({
                "error": result["error"]
            }), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500

# Add a debug endpoint to test API key
@app.route('/debug/api-key', methods=['GET'])
def debug_api_key():
    """Debug endpoint to test API key configuration"""
    try:
        api_key = os.environ.get('OPENROUTER_API_KEY', "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")
        
        # Test the API key with a simple request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/smart-hospital-system",
            "X-Title": "Smart Hospital AI Agent"
        }
        
        test_payload = {
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=test_payload,
            headers=headers
        )
        
        return jsonify({
            "api_key_format": f"{api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else 'TOO_SHORT'}",
            "api_key_length": len(api_key),
            "test_response_status": response.status_code,
            "test_response_headers": dict(response.headers),
            "test_successful": response.status_code == 200
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Debug test failed: {str(e)}",
            "api_key_format": f"{api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else 'TOO_SHORT'}",
            "api_key_length": len(api_key) if 'api_key' in locals() else 0
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
