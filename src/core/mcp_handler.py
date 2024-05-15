import os
import json
import base64
from typing import Dict, Any, List, Optional

import google.generativeai as genai
from google.generativeai.types import Tool

# MCP Tool Definitions
class MCPTools:
    @staticmethod
    def file_reader_tool() -> Tool:
        """Create a tool for reading files"""
        return Tool(
            function_declarations=[
                {
                    "name": "read_file",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the file to read"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            ]
        )
    
    @staticmethod
    def pdf_analyzer_tool() -> Tool:
        """Create a tool for analyzing PDF documents"""
        return Tool(
            function_declarations=[
                {
                    "name": "analyze_pdf",
                    "description": "Analyze a PDF document including text, tables, and images",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the PDF file to analyze"
                            },
                            "extract_tables": {
                                "type": "boolean",
                                "description": "Whether to extract tables from the PDF"
                            },
                            "extract_images": {
                                "type": "boolean",
                                "description": "Whether to extract images from the PDF"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            ]
        )
    
    @staticmethod
    def email_analyzer_tool() -> Tool:
        """Create a tool for analyzing email messages"""
        return Tool(
            function_declarations=[
                {
                    "name": "analyze_email",
                    "description": "Analyze an email message including headers, body, and attachments",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the email file to analyze"
                            },
                            "extract_attachments": {
                                "type": "boolean",
                                "description": "Whether to extract attachments from the email"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            ]
        )
    
    @staticmethod
    def web_search_tool() -> Tool:
        """Create a tool for web search"""
        return Tool(
            function_declarations=[
                {
                    "name": "web_search",
                    "description": "Search the web for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "num_results": {
                                "type": "integer",
                                "description": "The number of results to return"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        )

# MCP Handler Class
class MCPHandler:
    def __init__(self, model):
        self.model = model
        self.tools = {
            "read_file": self._read_file,
            "analyze_pdf": self._analyze_pdf,
            "analyze_email": self._analyze_email,
            "web_search": self._web_search
        }
    
    def get_all_tools(self) -> List[Tool]:
        """Get all available MCP tools"""
        return [
            MCPTools.file_reader_tool(),
            MCPTools.pdf_analyzer_tool(),
            MCPTools.email_analyzer_tool(),
            MCPTools.web_search_tool()
        ]
    
    async def process_with_mcp(self, prompt: str, document_paths: List[str]) -> str:
        """Process a request using MCP tools"""
        try:
            # Configure the model with tools
            model_with_tools = self.model.with_tools(self.get_all_tools())
            
            # Create the prompt with document references
            full_prompt = prompt
            for doc_path in document_paths:
                full_prompt += f"\nDocument path: {doc_path}"
            
            # Generate content with tool use
            response = model_with_tools.generate_content(full_prompt)
            
            # Process tool calls if any
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, 'tool_use_blocks') and part.tool_use_blocks:
                                for tool_use in part.tool_use_blocks:
                                    # Execute the tool and get the result
                                    tool_result = await self._execute_tool(tool_use)
                                    # Add the result to the prompt and regenerate
                                    full_prompt += f"\n\nTool result: {tool_result}"
            
            # Final generation with all tool results incorporated
            final_response = model_with_tools.generate_content(full_prompt)
            return final_response.text
        except Exception as e:
            return f"Error processing with MCP: {str(e)}"
    
    async def _execute_tool(self, tool_use: ToolUseBlock) -> str:
        """Execute a tool based on the tool use block"""
        try:
            tool_name = tool_use.name
            tool_params = json.loads(tool_use.args)
            
            if tool_name in self.tools:
                result = await self.tools[tool_name](**tool_params)
                return json.dumps(result)
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file and return its contents"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            with open(file_path, "rb") as f:
                content = f.read()
            
            # For text files, return the text content
            if file_path.lower().endswith((".txt", ".csv", ".json", ".xml", ".html")):
                try:
                    text_content = content.decode("utf-8")
                    return {"content": text_content, "mime_type": "text/plain"}
                except UnicodeDecodeError:
                    # If not a text file, return base64 encoded content
                    pass
            
            # For binary files, return base64 encoded content
            encoded_content = base64.b64encode(content).decode("utf-8")
            mime_type, _ = os.path.splitext(file_path)
            return {"content": encoded_content, "mime_type": mime_type, "encoding": "base64"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_pdf(self, file_path: str, extract_tables: bool = False, extract_images: bool = False) -> Dict[str, Any]:
        """Analyze a PDF document"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            # In a real implementation, you would use a PDF processing library
            # For this example, we'll just return a placeholder
            
            result = {
                "file_path": file_path,
                "analysis": "PDF analysis would be performed here",
            }
            
            if extract_tables:
                result["tables"] = ["Table 1 would be extracted here", "Table 2 would be extracted here"]
            
            if extract_images:
                result["images"] = ["Image 1 would be extracted here", "Image 2 would be extracted here"]
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_email(self, file_path: str, extract_attachments: bool = False) -> Dict[str, Any]:
        """Analyze an email message"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            # In a real implementation, you would use an email processing library
            # For this example, we'll just return a placeholder
            
            result = {
                "file_path": file_path,
                "headers": {
                    "from": "sender@example.com",
                    "to": "recipient@example.com",
                    "subject": "Email subject would be extracted here",
                    "date": "Email date would be extracted here",
                },
                "body": "Email body would be extracted here",
            }
            
            if extract_attachments:
                result["attachments"] = ["Attachment 1 would be extracted here", "Attachment 2 would be extracted here"]
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def _web_search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search the web for information"""
        try:
            # In a real implementation, you would use a web search API
            # For this example, we'll just return a placeholder
            
            results = [
                {
                    "title": f"Search result {i+1} for '{query}'",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"This is a snippet of search result {i+1} for '{query}'.",
                }
                for i in range(min(num_results, 10))
            ]
            
            return {
                "query": query,
                "results": results,
                "num_results": len(results),
            }
        except Exception as e:
            return {"error": str(e)}