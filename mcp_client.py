#!/usr/bin/env python3
"""
Multi-AI MCP Client
Connects multiple AI models (Claude, GPT-4, Gemini) to your MCP server
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import anthropic
import openai
from abc import ABC, abstractmethod

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class AIModel(ABC):
    """Base class for AI model integrations"""
    
    @abstractmethod
    async def chat(self, message: str, tools: List[Dict], system_prompt: str) -> str:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def available(self) -> bool:
        pass

class ClaudeModel(AIModel):
    """Claude AI model integration"""
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
    
    @property
    def name(self) -> str:
        return "Claude 3.5 Sonnet"
    
    @property
    def available(self) -> bool:
        return self.client is not None
    
    async def chat(self, message: str, tools: List[Dict], system_prompt: str) -> str:
        if not self.client:
            return "❌ Claude API key not configured"
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system_prompt,
                tools=tools,
                messages=[{"role": "user", "content": message}]
            )
            
            if response.content and response.content[0].type == "text":
                return response.content[0].text
            elif response.content and response.content[0].type == "tool_use":
                return f"🔧 Claude wants to use tool: {response.content[0].name}"
            
            return "❌ No response from Claude"
            
        except Exception as e:
            return f"❌ Claude error: {str(e)}"

class GPTModel(AIModel):
    """OpenAI GPT model integration"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
    
    @property
    def name(self) -> str:
        return "GPT-4"
    
    @property
    def available(self) -> bool:
        return self.client is not None
    
    async def chat(self, message: str, tools: List[Dict], system_prompt: str) -> str:
        if not self.client:
            return "❌ OpenAI API key not configured"
        
        try:
            # Convert MCP tools to OpenAI format
            openai_tools = []
            for tool in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["input_schema"]
                    }
                })
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                tools=openai_tools,
                max_tokens=2000
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            elif response.choices and response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                return f"🔧 GPT wants to use tool: {tool_call.function.name}"
            
            return "❌ No response from GPT"
            
        except Exception as e:
            return f"❌ GPT error: {str(e)}"

class GeminiModel(AIModel):
    """Google Gemini model integration (placeholder)"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
    
    @property
    def name(self) -> str:
        return "Gemini Pro"
    
    @property
    def available(self) -> bool:
        return self.api_key is not None
    
    async def chat(self, message: str, tools: List[Dict], system_prompt: str) -> str:
        return "🚧 Gemini integration coming soon..."

class LocalModel(AIModel):
    """Local model integration (Ollama/similar)"""
    
    def __init__(self):
        self.available_local = self._check_local_model()
    
    def _check_local_model(self) -> bool:
        # Check if Ollama or similar is running
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @property
    def name(self) -> str:
        return "Local Model (Ollama)"
    
    @property
    def available(self) -> bool:
        return self.available_local
    
    async def chat(self, message: str, tools: List[Dict], system_prompt: str) -> str:
        if not self.available:
            return "❌ Local model not available (Ollama not running?)"
        
        return "🚧 Local model integration coming soon..."

class MultiAIMCPClient:
    """MCP client that can use multiple AI models"""
    
    def __init__(self):
        self.models = {
            'claude': ClaudeModel(),
            'gpt': GPTModel(), 
            'gemini': GeminiModel(),
            'local': LocalModel()
        }
        self.available_tools = []
        self.current_model = None
        
    async def setup_mcp_tools(self):
        """Setup MCP server tools"""
        try:
            os.environ['MOCK_MODE'] = 'true'
            from developer_skill_analyzer.config import Config
            
            self.available_tools = [
                {
                    "name": "analyze_github_developer",
                    "description": "Analyze a developer's GitHub profile to extract skills and technical expertise",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "developer_name": {
                                "type": "string",
                                "description": "Full name of the developer to analyze"
                            }
                        },
                        "required": ["developer_name"]
                    }
                },
                {
                    "name": "find_skill_experts",
                    "description": "Find developers who are experts in a specific technology or skill",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "description": "Name of the skill or technology to find experts for"
                            }
                        },
                        "required": ["skill_name"]
                    }
                },
                {
                    "name": "get_all_employees",
                    "description": "Get list of all developers in the organization",
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_technical_stack", 
                    "description": "Get comprehensive technical stack and technology usage",
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup MCP tools: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available AI models"""
        return [name for name, model in self.models.items() if model.available]
    
    def set_model(self, model_name: str) -> bool:
        """Set the active AI model"""
        if model_name in self.models and self.models[model_name].available:
            self.current_model = model_name
            return True
        return False
    
    async def chat_with_ai(self, message: str, model_name: str = None) -> str:
        """Chat with specified AI model using MCP tools"""
        if model_name:
            if not self.set_model(model_name):
                return f"❌ Model '{model_name}' not available"
        
        if not self.current_model:
            available = self.get_available_models()
            if not available:
                return "❌ No AI models available"
            self.current_model = available[0]  # Use first available
        
        model = self.models[self.current_model]
        
        system_prompt = """You are an AI assistant helping with developer skill analysis. You have access to MCP tools that can analyze developer profiles, find skill experts, and provide team insights.

Available MCP tools:
- analyze_github_developer: Analyze a specific developer's skills
- find_skill_experts: Find developers expert in specific technologies  
- get_all_employees: List all team members
- get_technical_stack: Show all technologies used

Use these tools to provide accurate, data-driven responses about developers and skills."""
        
        return await model.chat(message, self.available_tools, system_prompt)
    
    async def compare_models(self, message: str) -> Dict[str, str]:
        """Get responses from all available models for comparison"""
        results = {}
        available_models = self.get_available_models()
        
        for model_name in available_models:
            print(f"🤖 Getting response from {self.models[model_name].name}...")
            response = await self.chat_with_ai(message, model_name)
            results[self.models[model_name].name] = response
        
        return results

async def main():
    """Main multi-AI MCP client interface"""
    print("🤖 MULTI-AI MCP CLIENT")
    print("=" * 50)
    print("🔗 Multiple AI models + Your MCP server")
    print()
    
    # Initialize client
    client = MultiAIMCPClient()
    
    if not await client.setup_mcp_tools():
        return
    
    # Check available models
    available = client.get_available_models()
    
    print("🤖 AVAILABLE AI MODELS:")
    for model_name in client.models:
        model = client.models[model_name]
        status = "✅" if model.available else "❌"
        print(f"{status} {model.name}")
    print()
    
    if not available:
        print("❌ No AI models available!")
        print("💡 Set API keys:")
        print("   $env:ANTHROPIC_API_KEY='your-claude-key'")
        print("   $env:OPENAI_API_KEY='your-openai-key'")
        print("   $env:GOOGLE_API_KEY='your-gemini-key'")
        print()
        print("🔄 FALLBACK MODE: Direct MCP Server Access")
        print("✅ You can still test your MCP server functionality!")
        print()
        
        # Add fallback mode for direct MCP interaction
        print("💬 AVAILABLE COMMANDS:")
        print("• 'employees' - List all developers")
        print("• 'stack' - Show technical stack")
        print("• 'analyze <name>' - Analyze developer skills")
        print("• 'experts <skill>' - Find skill experts")
        print("• 'help' - Show this help")
        print()
        
        while True:
            try:
                user_input = input("🛠️  MCP Direct: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'employees':
                    result = await client.call_mcp_tool("get_all_employees", {})
                    if result["success"]:
                        employees = result["data"]
                        print("\n👥 **Team Members:**")
                        for i, emp in enumerate(employees, 1):
                            print(f"{i}. **{emp['name']}** - {emp['role']} ({emp['team']} Team)")
                    else:
                        print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    continue
                
                if user_input.lower() == 'stack':
                    result = await client.call_mcp_tool("get_technical_stack", {})
                    if result["success"]:
                        stack = result["data"]
                        print("\n🛠️ **Technical Stack:**")
                        if "summary" in stack:
                            summary = stack["summary"]
                            print(f"**Total Technologies:** {summary.get('total_technologies', 'N/A')}")
                        if "stack" in stack:
                            for category, items in stack["stack"].items():
                                print(f"\n**{category.replace('_', ' ').title()}:**")
                                for item in items[:3]:  # Top 3 per category
                                    print(f"• {item['name']}: {item['usage_percentage']}% usage")
                    else:
                        print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    continue
                
                if user_input.lower().startswith('analyze '):
                    name = user_input[8:].strip()
                    if name:
                        result = await client.call_mcp_tool("analyze_github_developer", {"developer_name": name})
                        if result["success"]:
                            analysis = result["data"]
                            print(f"\n🔍 **Skills Analysis for {name}:**")
                            if "summary" in analysis:
                                summary = analysis["summary"]
                                print(f"**Primary Language:** {summary.get('primary_language', 'N/A')}")
                                print(f"**Total Commits:** {summary.get('total_commits', 'N/A')}")
                                print(f"**Activity Level:** {summary.get('activity_level', 'N/A')}")
                            if "technical_skills" in analysis:
                                print("\n**🎯 Technical Skills:**")
                                for skill in analysis["technical_skills"][:5]:
                                    print(f"• {skill['skill']}: {skill['level']} ({skill['confidence']}%)")
                        else:
                            print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    else:
                        print("❌ Please specify a developer name")
                    continue
                
                if user_input.lower().startswith('experts '):
                    skill = user_input[8:].strip()
                    if skill:
                        result = await client.call_mcp_tool("find_skill_experts", {"skill_name": skill})
                        if result["success"]:
                            experts = result["data"]
                            if experts:
                                print(f"\n🎯 **{skill.title()} Experts:**")
                                for expert in experts[:5]:
                                    print(f"**{expert['name']}** ({expert['team']} Team)")
                                    print(f"└─ {expert['skill']}: {expert['level']} ({expert['confidence']}% confidence)")
                            else:
                                print(f"❌ No experts found for {skill}")
                        else:
                            print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    else:
                        print("❌ Please specify a skill")
                    continue
                
                if user_input.lower() in ['help', 'h']:
                    print("\n💡 MCP Direct Commands:")
                    print("• 'employees' - List all developers")
                    print("• 'stack' - Show technical stack")
                    print("• 'analyze <name>' - Analyze developer skills")
                    print("• 'experts <skill>' - Find skill experts")
                    print("• 'help' - Show this help")
                    print("• 'quit' - Exit")
                    continue
                
                if not user_input:
                    continue
                
                print(f"❓ Unknown command: '{user_input}'")
                print("Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return
    
    print(f"🎯 DEFAULT MODEL: {client.models[available[0]].name}")
    print()
    print("💬 COMMANDS:")
    print("• 'use claude' - Switch to Claude")
    print("• 'use gpt' - Switch to GPT-4")
    print("• 'compare <question>' - Get responses from all models")
    print("• 'models' - Show available models")
    print("• 'help' - Show this help")
    print()
    
    while True:
        try:
            user_input = input("🤖 Multi-AI: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'models':
                print("\n🤖 Available Models:")
                for model_name in available:
                    current = "👉" if model_name == client.current_model else "  "
                    print(f"{current} {client.models[model_name].name}")
                continue
            
            if user_input.lower().startswith('use '):
                model_name = user_input[4:].strip().lower()
                if client.set_model(model_name):
                    print(f"✅ Switched to {client.models[model_name].name}")
                else:
                    print(f"❌ Model '{model_name}' not available")
                continue
            
            if user_input.lower().startswith('compare '):
                question = user_input[8:].strip()
                if question:
                    print(f"\n🔄 Comparing responses to: '{question}'")
                    print("=" * 50)
                    
                    results = await client.compare_models(question)
                    
                    for model_name, response in results.items():
                        print(f"\n🤖 **{model_name}:**")
                        print(response)
                        print("-" * 30)
                continue
            
            if user_input.lower() in ['help', 'h']:
                print("\n💡 Multi-AI MCP Commands:")
                print("• Just ask questions naturally")
                print("• 'use <model>' - Switch AI model")
                print("• 'compare <question>' - Compare all models")
                print("• 'models' - List available models")
                continue
            
            if not user_input:
                continue
            
            # Chat with current model
            current_name = client.models[client.current_model].name if client.current_model else "Unknown"
            print(f"\n🤖 {current_name} is thinking...")
            
            response = await client.chat_with_ai(user_input)
            print(f"\n**{current_name}:** {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())