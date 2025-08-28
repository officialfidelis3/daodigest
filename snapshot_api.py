import requests
import logging
from typing import Dict, Any, Optional

# Snapshot GraphQL API endpoint
SNAPSHOT_API_URL = "https://hub.snapshot.org/graphql"

def fetch_dao_proposals(dao_name: str, limit: int = 10) -> Optional[Dict[str, Any]]:
    """
    Fetch recent proposals for a given DAO from Snapshot.org
    
    Args:
        dao_name: The name/ID of the DAO (e.g., 'uniswap', 'makerdao')
        limit: Maximum number of proposals to fetch
        
    Returns:
        Dictionary containing proposals data or None if failed
    """
    
    # GraphQL query to fetch proposals
    query = """
    query Proposals($space: String!, $first: Int!) {
        proposals(
            first: $first,
            where: {
                space: $space
            },
            orderBy: "created",
            orderDirection: desc
        ) {
            id
            title
            body
            choices
            start
            end
            state
            author
            scores
            scores_total
            votes
            created
            link
        }
    }
    """
    
    variables = {
        "space": dao_name.lower(),
        "first": limit
    }
    
    try:
        logging.info(f"Fetching proposals for DAO: {dao_name}")
        
        response = requests.post(
            SNAPSHOT_API_URL,
            json={
                "query": query,
                "variables": variables
            },
            headers={
                "Content-Type": "application/json",
                "User-Agent": "DAO-Governance-Explorer/1.0"
            },
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            logging.error(f"GraphQL errors: {data['errors']}")
            raise Exception(f"API returned errors: {data['errors']}")
        
        proposals = data.get("data", {}).get("proposals", [])
        
        # Format proposals for easier use
        formatted_proposals = []
        for proposal in proposals:
            # Create Snapshot URL
            snapshot_url = f"https://snapshot.org/#/{dao_name.lower()}/proposal/{proposal['id']}"
            
            formatted_proposal = {
                "id": proposal["id"],
                "title": proposal["title"],
                "body": proposal["body"],
                "choices": proposal["choices"],
                "state": proposal["state"],
                "author": proposal["author"],
                "created": proposal["created"],
                "start": proposal["start"],
                "end": proposal["end"],
                "votes": proposal["votes"],
                "scores": proposal["scores"],
                "scores_total": proposal["scores_total"],
                "link": snapshot_url,
                "original_link": proposal.get("link", snapshot_url)
            }
            formatted_proposals.append(formatted_proposal)
        
        logging.info(f"Successfully fetched {len(formatted_proposals)} proposals for {dao_name}")
        
        return {
            "dao_name": dao_name,
            "proposals": formatted_proposals
        }
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error fetching proposals: {e}")
        raise Exception(f"Failed to connect to Snapshot API: {str(e)}")
    except Exception as e:
        logging.error(f"Error processing proposals: {e}")
        raise Exception(f"Failed to fetch proposals: {str(e)}")

def get_popular_daos():
    """Return a list of popular DAO names with their correct Snapshot space IDs"""
    return [
        {"id": "ens.eth", "display": "ENS"},
        {"id": "gitcoindao.eth", "display": "Gitcoin"},
        {"id": "balancer.eth", "display": "Balancer"},
        {"id": "arbitrumfoundation.eth", "display": "Arbitrum"},
        {"id": "aave.eth", "display": "Aave"},
        {"id": "uniswapgovernance.eth", "display": "Uniswap"},
        {"id": "makerdao.eth", "display": "MakerDAO"},
        {"id": "compound-community.eth", "display": "Compound"},
        {"id": "sushigov.eth", "display": "SushiSwap"},
        {"id": "curve.eth", "display": "Curve"},
        {"id": "olympusdao.eth", "display": "OlympusDAO"},
        {"id": "banklessvault.eth", "display": "BanklessDAO"},
        {"id": "nouns.eth", "display": "Nouns"}
    ]
