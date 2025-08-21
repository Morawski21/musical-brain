"""
Generic CRUD operations for Musical Brain entities.
"""

import logging
import uuid
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from musical_brain.database import db

logger = logging.getLogger(__name__)


async def create_node(label: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new node with the given label and data."""
    node_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    logger.info(f"Creating {label} node with ID: {node_id}")
    
    # Prepare node data with ID and timestamps
    node_data = {
        "id": node_id,
        "created_at": now,
        **data
    }
    
    # Add updated_at for nodes that support it
    if label in ["Album"]:
        node_data["updated_at"] = now
    
    # Convert datetime objects to ISO strings for Neo4j
    for key, value in node_data.items():
        if isinstance(value, datetime):
            node_data[key] = value.isoformat()
    
    query = f"""
    CREATE (n:{label} $props)
    RETURN n
    """
    
    result = await db.run_query(query, {"props": node_data})
    if result:
        logger.info(f"Successfully created {label} node: {node_id}")
        return dict(result[0]["n"])
    logger.error(f"Failed to create {label} node with ID: {node_id}")
    raise RuntimeError(f"Failed to create {label} node")


async def get_node(label: str, node_id: str) -> Optional[Dict[str, Any]]:
    """Get a node by label and ID."""
    logger.debug(f"Fetching {label} node with ID: {node_id}")
    query = f"""
    MATCH (n:{label} {{id: $id}})
    RETURN n
    """
    
    result = await db.run_query(query, {"id": node_id})
    if result:
        logger.debug(f"Found {label} node: {node_id}")
        return dict(result[0]["n"])
    logger.debug(f"{label} node not found: {node_id}")
    return None


async def update_node(label: str, node_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update a node with partial data."""
    logger.info(f"Updating {label} node {node_id} with {len(updates)} fields")
    if not updates:
        logger.debug(f"No updates provided for {label} node: {node_id}")
        return await get_node(label, node_id)
    
    # Add updated_at timestamp for applicable nodes
    if label in ["Album"]:
        updates["updated_at"] = datetime.now(UTC).isoformat()
    
    # Convert datetime objects to ISO strings for Neo4j
    for key, value in updates.items():
        if isinstance(value, datetime):
            updates[key] = value.isoformat()
    
    # Build SET clause dynamically
    set_parts = [f"n.{key} = $updates.{key}" for key in updates.keys()]
    set_clause = ", ".join(set_parts)
    
    query = f"""
    MATCH (n:{label} {{id: $id}})
    SET {set_clause}
    RETURN n
    """
    
    result = await db.run_query(query, {"id": node_id, "updates": updates})
    if result:
        logger.info(f"Successfully updated {label} node: {node_id}")
        return dict(result[0]["n"])
    logger.warning(f"Failed to update {label} node (not found?): {node_id}")
    return None


async def delete_node(label: str, node_id: str) -> bool:
    """Delete a node by label and ID."""
    logger.info(f"Deleting {label} node: {node_id}")
    query = f"""
    MATCH (n:{label} {{id: $id}})
    DELETE n
    RETURN count(n) as deleted_count
    """
    
    result = await db.run_query(query, {"id": node_id})
    success = result and result[0]["deleted_count"] > 0
    if success:
        logger.info(f"Successfully deleted {label} node: {node_id}")
    else:
        logger.warning(f"Failed to delete {label} node (not found?): {node_id}")
    return success


async def list_nodes(label: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """List nodes of a given label with pagination."""
    logger.debug(f"Listing {label} nodes (limit={limit}, offset={offset})")
    query = f"""
    MATCH (n:{label})
    RETURN n
    ORDER BY n.created_at DESC
    SKIP $offset
    LIMIT $limit
    """
    
    result = await db.run_query(query, {"limit": limit, "offset": offset})
    nodes = [dict(record["n"]) for record in result]
    logger.debug(f"Found {len(nodes)} {label} nodes")
    return nodes


async def count_nodes(label: str) -> int:
    """Count total number of nodes with given label."""
    query = f"""
    MATCH (n:{label})
    RETURN count(n) as total
    """
    
    result = await db.run_query(query)
    return result[0]["total"] if result else 0


async def initialize_schema():
    """Create constraints and indexes for the graph schema."""
    constraints_and_indexes = [
        # Unique constraints for IDs
        "CREATE CONSTRAINT album_id_unique IF NOT EXISTS FOR (a:Album) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT artist_id_unique IF NOT EXISTS FOR (a:Artist) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT genre_id_unique IF NOT EXISTS FOR (g:Genre) REQUIRE g.id IS UNIQUE",
        
        # Indexes for common search fields
        "CREATE INDEX album_title_index IF NOT EXISTS FOR (a:Album) ON (a.title)",
        "CREATE INDEX artist_name_index IF NOT EXISTS FOR (a:Artist) ON (a.name)",
        "CREATE INDEX genre_name_index IF NOT EXISTS FOR (g:Genre) ON (g.name)",
        
        # Index for date-based queries
        "CREATE INDEX album_created_at_index IF NOT EXISTS FOR (a:Album) ON (a.created_at)",
    ]
    
    for constraint_or_index in constraints_and_indexes:
        try:
            await db.run_query(constraint_or_index)
        except Exception as e:
            logger.debug(f"Schema setup note: {e}")
    
    logger.info("Graph schema initialized successfully")