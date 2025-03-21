import os
import logging
from mcp.server.fastmcp import FastMCP
from linear_mcp.linear_service import LinearIssueState, linear_service, LinearIssue, LinearComment
from linear_mcp.server_logger import logger, configure_logging
from typing import Dict, List, Any
from argparse import ArgumentParser
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

def init(mcp_server, args):

    team_id = args.team_id or os.getenv("LINEAR_TEAM_ID", None)

    # MCP resources and tools
    @mcp_server.tool()
    async def get_issues() -> List[LinearIssue]:
        """Get all Linear issues"""
        return await linear_service.get_issues()

    @mcp_server.tool()
    async def get_issue(issue_id: str) -> LinearIssue:
        """Get a specific Linear issue by ID"""
        return await linear_service.get_issue(issue_id)

    @mcp_server.tool()
    async def get_issue_comments(issue_id: str) -> List[LinearComment]:
        """Get comments for a specific Linear issue"""
        return await linear_service.get_issue_comments(issue_id)

    @mcp_server.tool()
    async def search_issues(query_string : str) -> List[LinearIssue]:
        """Search for Linear issues based on a query string"""
        return await linear_service.search_issues(query_string, query_string)

    if team_id:
        @mcp_server.tool()
        async def create_issue(title: str, description: str) -> LinearIssue:
            """Create a new Linear issue"""
            return await linear_service.create_issue(title, description, team_id = team_id)
    else:
        @mcp_server.tool()
        async def create_issue(title: str, description: str, team_id: str) -> LinearIssue:
            """Create a new Linear issue"""
            return await linear_service.create_issue(title, description, team_id)

    @mcp_server.tool()
    async def update_issue_description(issue_id: str, description: str) -> LinearIssue:
        """Update the description of a Linear issue"""
        return await linear_service.update_issue_description(issue_id, description)

    @mcp_server.tool()
    async def add_comment(issue_id: str, body: str) -> LinearComment:
        """Add a comment to a Linear issue"""
        return await linear_service.add_comment(issue_id, body)

    @mcp_server.tool()
    async def assign_issue(issue_id: str, assignee_id: str) -> LinearIssue:
        """Assign a Linear issue to a user"""
        return await linear_service.assign_issue(issue_id, assignee_id)


    @mcp_server.resource("states://list_issue_states", mime_type = "application/json")
    async def list_issue_states_resource() -> List[LinearIssueState]:
        """List all issue states"""
        return await linear_service.list_issue_states()
    
    @mcp_server.tool()
    async def list_issue_states() -> List[LinearIssueState]:
        """List all issue states"""
        return await linear_service.list_issue_states()

    @mcp_server.tool()
    async def change_issue_state(issue_id: str, state_id: str) -> LinearIssue:
        """Change the state of a Linear issue"""
        return await linear_service.change_issue_state(issue_id, state_id)

    @mcp_server.resource("teams://get_teams", mime_type = "application/json")
    async def get_teams_resource() -> List[Dict[str, Any]]:
        """Get all teams in Linear"""
        return await linear_service.get_teams()
    
    @mcp_server.tool()
    async def get_teams() -> List[Dict[str, Any]]:
        """Get all teams in Linear"""
        return await linear_service.get_teams()

    if team_id:
        @mcp_server.resource("teams://get_team_members", mime_type = "application/json")
        async def get_team_members_resource() -> List[Dict[str, Any]]:
            """Get all members of a specific team"""
            return await linear_service.get_team_members(team_id = team_id)
    else:
        @mcp_server.resource("teams://{team_id}//get_team_members", mime_type = "application/json")
        async def get_team_members_resource(team_id: str) -> List[Dict[str, Any]]:
            """Get all members of a specific team"""
            return await linear_service.get_team_members(team_id)
    
    if team_id:
        @mcp_server.tool()
        async def get_team_members() -> List[Dict[str, Any]]:
            """Get all members of a specific team"""
            return await linear_service.get_team_members(team_id = team_id)
    else:
        @mcp_server.tool()
        async def get_team_members(team_id: str) -> List[Dict[str, Any]]:
            """Get all members of a specific team"""
            return await linear_service.get_team_members(team_id)

    @mcp_server.prompt()
    def linear_issue_prompt(issue_id: str) -> str:
        """Create a prompt to analyze a Linear issue"""
        return f"""
        Please analyze the Linear issue with ID {issue_id}. 
        Consider the following aspects:
        - Is the issue description clear and complete?
        - Are there any missing details that should be added?
        - What would be the best approach to solve this issue?
        - Are there any potential blockers or dependencies?
        """

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--linear-api-key", type=str, required=False, default=None)
    parser.add_argument("--team_id", type=str, required=False, default=None)
    args = parser.parse_args()
    return args

def configure_api_key(args):
    linear_api_key = args.linear_api_key or os.getenv("LINEAR_API_KEY")
    if not linear_api_key:
        raise ValueError("Linear API key is required. Please set the LINEAR_API_KEY environment variable or use the --linear-api-key flag.")
    linear_service.set_api_key(linear_api_key)

def configure_server_logging():
    log_level = os.getenv("LINEAR_LOG_LEVEL", "INFO")
    log_file = os.getenv("LINEAR_LOG_FILE", "linear_api.log")
    configure_logging(level=log_level, log_file=log_file)

def main():
    try:
        args = parse_args()
        configure_server_logging()
        configure_api_key(args)
        
        # Initialize MCP server after all configuration is done
        logger.info("Starting Linear MCP server")
        mcp = FastMCP("Linear")
        init(mcp, args)

        # Run the server using SSE transport
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()