import json
import httpx
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
from linear_mcp.server_logger import logger

# Linear API base URL
LINEAR_API_URL = "https://api.linear.app/graphql"

# Models for Linear API
class LinearIssue(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    assignee: Optional[Dict[str, Any]] = None
    team: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    
class LinearComment(BaseModel):
    id: str
    body: str
    user: Optional[Dict[str, Any]] = None
    createdAt: str


class LinearIssueState(BaseModel):
    id: str
    name: str

class LinearClient:
    def __init__(self):
        self.api_key = None
        self.headers = None
    
    def set_api_key(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"{api_key}",
            "Content-Type": "application/json"
        }
    
    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query against the Linear API"""

        if not self.api_key:
            raise ValueError("Linear API key is not set.")
        if not self.headers:
            raise ValueError("Headers are not set.")

        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        # Log the request (without the full query for brevity)
        logger.info(f"Executing GraphQL query with variables: {json.dumps(variables or {})}")
        logger.debug(f"Full query: {query}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    LINEAR_API_URL,
                    headers=self.headers,
                    json=payload
                )
                
                # Log response status
                logger.info(f"Response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_message = f"Linear API error: {response.text}"
                    logger.error(error_message)
                    raise Exception(error_message)
                
                response_data = response.json()
                
                # Check for GraphQL errors
                if "errors" in response_data:
                    error_message = f"GraphQL errors: {json.dumps(response_data['errors'])}"
                    logger.error(error_message)
                    # Still return the response as it might contain partial data
                    logger.debug(f"Response data: {json.dumps(response_data)}")
                    return response_data
                
                # Log success (with limited data for brevity)
                if "data" in response_data:
                    data_keys = list(response_data["data"].keys())
                    logger.info(f"Successful response with data keys: {data_keys}")
                    logger.debug(f"Full response data: {json.dumps(response_data)}")
                
                return response_data
        except Exception as e:
            error_message = f"Error executing GraphQL query: {str(e)}"
            logger.exception(error_message)
            raise

class LinearService:
    def __init__(self, client: LinearClient = None):
        self.client = client or LinearClient()
    
    def set_api_key(self, api_key: str):
        self.client.set_api_key(api_key)

    async def get_issues(self) -> List[LinearIssue]:
        """Get all Linear issues"""
        logger.info("Getting all issues")
        query = """
        query {
            issues {
                nodes {
                    id
                    title
                    description
                    state {
                        id
                        name
                    }
                    assignee {
                        id
                        name
                    }
                    team {
                        id
                        name
                    }
                    priority
                }
            }
        }
        """
        
        try:
            result = await self.client.execute_query(query)
            issues = result.get("data", {}).get("issues", {}).get("nodes", [])
            logger.info(f"Retrieved {len(issues)} issues")
            return [LinearIssue(**issue) for issue in issues]
        except Exception as e:
            logger.exception("Error getting issues")
            raise

    async def get_issue(self, issue_id: str) -> LinearIssue:
        """Get a specific Linear issue by ID"""
        logger.info(f"Getting issue with ID: {issue_id}")
        query = """
        query($id: String!) {
            issue(id: $id) {
                id
                title
                description
                state {
                    id
                    name
                }
                assignee {
                    id
                    name
                }
                team {
                    id
                    name
                }
                priority
            }
        }
        """
        
        variables = {"id": issue_id}
        try:
            result = await self.client.execute_query(query, variables)
            issue_data = result.get("data", {}).get("issue", {})
            
            if not issue_data:
                error_message = f"Issue with ID {issue_id} not found"
                logger.error(error_message)
                raise ValueError(error_message)
            
            logger.info(f"Retrieved issue: {issue_data.get('title', 'Unknown title')}")
            return LinearIssue(**issue_data)
        except Exception as e:
            logger.exception(f"Error getting issue with ID {issue_id}")
            raise

    async def get_issue_comments(self, issue_id: str) -> List[LinearComment]:
        """Get comments for a specific Linear issue"""
        logger.info(f"Getting comments for issue with ID: {issue_id}")
        query = """
        query($id: String!) {
            issue(id: $id) {
                comments {
                    nodes {
                        id
                        body
                        user {
                            id
                            name
                        }
                        createdAt
                    }
                }
            }
        }
        """
        
        variables = {"id": issue_id}
        try:
            result = await self.client.execute_query(query, variables)
            comments = result.get("data", {}).get("issue", {}).get("comments", {}).get("nodes", [])
            
            logger.info(f"Retrieved {len(comments)} comments for issue {issue_id}")
            return [LinearComment(**comment) for comment in comments]
        except Exception as e:
            logger.exception(f"Error getting comments for issue with ID {issue_id}")
            raise

    async def search_issues(self, description_contains: Optional[str] = None, title_contains: Optional[str] = None) -> List[LinearIssue]:
        """Search for Linear issues based on a query string"""
        logger.info(f"Searching issues with description containing: {description_contains} or title containing: {title_contains}")
        
        # Build filter based on provided parameters
        filter_parts = []
        if description_contains:
            filter_parts.append({"description": {"containsIgnoreCase": description_contains}})
        if title_contains:
            filter_parts.append({"title": {"containsIgnoreCase": title_contains}})
        
        # Construct the filter object
        filter_obj = {}
        if len(filter_parts) > 1:
            filter_obj = {"or": filter_parts}
        elif len(filter_parts) == 1:
            filter_obj = filter_parts[0]
        
        query = """
        query($filter: IssueFilter) {
            issues(filter: $filter, first: 10) {
                nodes {
                    id
                    title
                    description
                    state {
                        id
                        name
                    }
                    assignee {
                        id
                        name
                    }
                    team {
                        id
                        name
                    }
                    priority
                }
            }
        }
        """
        
        variables = {"filter": filter_obj}
        try:
            result = await self.client.execute_query(query, variables)
            logger.info(f"Result: {result}")
            issues = result.get("data", {}).get("issues", {}).get("nodes", [])
            
            logger.info(f"Found {len(issues)} issues matching query")
            return [LinearIssue(**issue) for issue in issues]
        except Exception as e:
            logger.exception(f"Error searching issues")
            raise
    async def create_issue(self, title: str, description: str, team_id: str) -> LinearIssue:
        """Create a new Linear issue"""
        logger.info(f"Creating new issue: {title} for team: {team_id}")
        query = """
        mutation($title: String!, $description: String, $teamId: String!) {
            issueCreate(input: {
                title: $title,
                description: $description,
                teamId: $teamId
            }) {
                issue {
                    id
                    title
                    description
                    state {
                        id
                        name
                    }
                    team {
                        id
                        name
                    }
                    priority
                }
            }
        }
        """
        
        variables = {
            "title": title,
            "description": description,
            "teamId": team_id
        }
        
        try:
            result = await self.client.execute_query(query, variables)
            issue_data = result.get("data", {}).get("issueCreate", {}).get("issue", {})
            
            if not issue_data:
                error_message = "Failed to create issue"
                logger.error(error_message)
                raise ValueError(error_message)
            
            logger.info(f"Created issue with ID: {issue_data.get('id')}")
            return LinearIssue(**issue_data)
        except Exception as e:
            logger.exception(f"Error creating issue: {title}")
            raise

    async def update_issue_description(self, issue_id: str, description: str) -> LinearIssue:
        """Update the description of a Linear issue"""
        logger.info(f"Updating description for issue with ID: {issue_id}")
        query = """
        mutation($id: String!, $description: String!) {
            issueUpdate(id: $id, input: {
                description: $description
            }) {
                issue {
                    id
                    title
                    description
                    state {
                        id
                        name
                    }
                    assignee {
                        id
                        name
                    }
                    team {
                        id
                        name
                    }
                    priority
                }
            }
        }
        """
        
        variables = {
            "id": issue_id,
            "description": description
        }
        
        try:
            result = await self.client.execute_query(query, variables)
            issue_data = result.get("data", {}).get("issueUpdate", {}).get("issue", {})
            
            if not issue_data:
                error_message = f"Failed to update issue with ID {issue_id}"
                logger.error(error_message)
                raise ValueError(error_message)
            
            logger.info(f"Updated description for issue: {issue_data.get('title')}")
            return LinearIssue(**issue_data)
        except Exception as e:
            logger.exception(f"Error updating description for issue with ID {issue_id}")
            raise

    async def add_comment(self, issue_id: str, body: str) -> LinearComment:
        """Add a comment to a Linear issue"""
        logger.info(f"Adding comment to issue with ID: {issue_id}")
        query = """
        mutation($issueId: String!, $body: String!) {
            commentCreate(input: {
                issueId: $issueId,
                body: $body
            }) {
                comment {
                    id
                    body
                    user {
                        id
                        name
                    }
                    createdAt
                }
            }
        }
        """
        
        variables = {
            "issueId": issue_id,
            "body": body
        }
        
        try:
            result = await self.client.execute_query(query, variables)
            comment_data = result.get("data", {}).get("commentCreate", {}).get("comment", {})
            
            if not comment_data:
                error_message = f"Failed to add comment to issue with ID {issue_id}"
                logger.error(error_message)
                raise ValueError(error_message)
            
            logger.info(f"Added comment with ID: {comment_data.get('id')} to issue: {issue_id}")
            return LinearComment(**comment_data)
        except Exception as e:
            logger.exception(f"Error adding comment to issue with ID {issue_id}")
            raise

    async def assign_issue(self, issue_id: str, assignee_id: str) -> LinearIssue:
        """Assign a Linear issue to a user"""
        logger.info(f"Assigning issue {issue_id} to user {assignee_id}")
        query = """
        mutation($id: String!, $assigneeId: String!) {
            issueUpdate(id: $id, input: {
                assigneeId: $assigneeId
            }) {
                issue {
                    id
                    title
                    description
                    state {
                        id
                        name
                    }
                    assignee {
                        id
                        name
                    }
                    team {
                        id
                        name
                    }
                    priority
                }
            }
        }
        """
        
        variables = {
            "id": issue_id,
            "assigneeId": assignee_id
        }
        
        try:
            result = await self.client.execute_query(query, variables)
            issue_data = result.get("data", {}).get("issueUpdate", {}).get("issue", {})
            
            if not issue_data:
                error_message = f"Failed to assign issue with ID {issue_id}"
                logger.error(error_message)
                raise ValueError(error_message)
            
            assignee_name = issue_data.get("assignee", {}).get("name", "Unknown")
            logger.info(f"Assigned issue {issue_id} to {assignee_name}")
            return LinearIssue(**issue_data)
        except Exception as e:
            logger.exception(f"Error assigning issue {issue_id} to user {assignee_id}")
            raise

    async def list_issue_states(self) -> List[LinearIssueState]:
        """Get all issue states"""
        logger.info("Getting all issue states")
        query = """
        query {
            workflowStates {
                nodes {
                    id
                    name
                }
            }
        }
        """
        try:
            result = await self.client.execute_query(query)
            states = result.get("data", {}).get("workflowStates", {}).get("nodes", [])
            return [LinearIssueState(**state) for state in states]
        except Exception as e:
            logger.exception("Error getting issue states")
            raise

    async def change_issue_state(self, issue_id: str, state_id: str) -> LinearIssue:
        """Change the state of a Linear issue"""
        logger.info(f"Changing state of issue {issue_id} to state {state_id}")
        query = """
        mutation($id: String!, $stateId: String!) {
            issueUpdate(id: $id, input: {
                stateId: $stateId
            }) {
                issue {
                    id
                    title
                    description
                    state {
                        id
                        name
                    }
                    assignee {
                        id
                        name
                    }
                    team {
                        id
                        name
                    }
                    priority
                }
            }
        }
        """
        
        variables = {
            "id": issue_id,
            "stateId": state_id
        }
        
        try:
            result = await self.client.execute_query(query, variables)
            issue_data = result.get("data", {}).get("issueUpdate", {}).get("issue", {})
            
            if not issue_data:
                error_message = f"Failed to change state of issue with ID {issue_id}"
                logger.error(error_message)
                raise ValueError(error_message)
            
            state_name = issue_data.get("state", {}).get("name", "Unknown")
            logger.info(f"Changed state of issue {issue_id} to {state_name}")
            return LinearIssue(**issue_data)
        except Exception as e:
            logger.exception(f"Error changing state of issue {issue_id} to state {state_id}")
            raise

    async def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams in Linear"""
        logger.info("Getting all teams")
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    key
                }
            }
        }
        """
        
        try:
            result = await self.client.execute_query(query)
            teams = result.get("data", {}).get("teams", {}).get("nodes", [])
            
            logger.info(f"Retrieved {len(teams)} teams")
            return teams
        except Exception as e:
            logger.exception("Error getting teams")
            raise

    async def get_team_members(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all members of a specific team"""
        logger.info(f"Getting members for team with ID: {team_id}")
        query = """
        query($id: String!) {
            team(id: $id) {
                members {
                    nodes {
                        id
                        name
                        email
                    }
                }
            }
        }
        """
        
        variables = {"id": team_id}
        try:
            result = await self.client.execute_query(query, variables)
            members = result.get("data", {}).get("team", {}).get("members", {}).get("nodes", [])
            
            logger.info(f"Retrieved {len(members)} members for team {team_id}")
            return members
        except Exception as e:
            logger.exception(f"Error getting members for team with ID {team_id}")
            raise

# Create a singleton instance for easy import
linear_service = LinearService()