import os
from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Student Deadline Tracker File Reader")

@mcp.tool
def read_uploaded_file(file_path: str) -> str:
    """
    Reads the content of an uploaded student text file (e.g., syllabus, text document) containing deadlines.
    
    Args:
        file_path (str): The local path to the text file to be read.
        
    Returns:
        str: The contents of the text file, or an error message.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    # Start FastMCP server (default transport is stdio)
    mcp.run()
