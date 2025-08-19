# Music Knowledge Graph Implementation Plan

## System Overview

A self-hosted music knowledge graph system for organizing album reviews, artist relationships, and musical influences. Built with Neo4j for graph storage, Python FastAPI for the backend, and a simple web interface for note-taking.

## Architecture

```
Desktop/Web Browser
        ↓ (HTTPS REST API)
FastAPI Backend (Python)
        ↓ (Cypher Queries)
Neo4j Graph Database
        ↓ (Docker Network)
NAS/Self-Hosted Environment
```

## Tech Stack

### Core Components
- **Database**: Neo4j Community Edition (Docker)
- **Backend API**: Python FastAPI
- **Frontend**: Simple web interface (HTML/CSS/JS)
- **Deployment**: Docker Compose on NAS
- **Authentication**: Basic auth

### Python Dependencies
```
fastapi
uvicorn
neo4j
pydantic
```

## Neo4j Graph Schema

### Node Types

#### Album
```cypher
CREATE (:Album {
    id: string,
    title: string,
    album_type: string, // LP, EP, Single, Live, Compilation
    release_year: integer,
    review_score: float, // 0.0 to 5.0 (0.1 intervals)
    review_notes: string,
    review_date: date,
    aoty_score: float,
    rym_score: float,
    created_at: datetime,
    updated_at: datetime
})
```

#### Artist
```cypher
CREATE (:Artist {
    id: string,
    name: string,
    country: string,
    formed_year: integer,
    notes: string,
    created_at: datetime
})
```

#### Genre
```cypher
CREATE (:Genre {
    id: string,
    name: string,
    description: string
})
```

#### Label
```cypher
CREATE (:Label {
    id: string,
    name: string,
    country: string,
    founded_year: integer
})
```

#### Contributor
```cypher
CREATE (:Contributor {
    id: string,
    name: string,
    role: string, // Producer, Engineer, Songwriter, etc.
    notes: string
})
```

### Relationship Types

#### Artist Relationships
- `(Artist)-[:CREATED]->(Album)`
- `(Artist)-[:INFLUENCED_BY]->(Artist)`
- `(Artist)-[:COLLABORATED_WITH]->(Artist)`
- `(Artist)-[:MEMBER_OF]->(Artist)` // for bands

#### Album Relationships
- `(Album)-[:BELONGS_TO_GENRE]->(Genre)`
- `(Album)-[:RELEASED_BY]->(Label)`
- `(Album)-[:CONTRIBUTED_BY]->(Contributor)`
- `(Album)-[:INFLUENCED_BY]->(Album)`
- `(Album)-[:SIMILAR_TO]->(Album)`

#### Additional Relationships
- `(Genre)-[:SUBGENRE_OF]->(Genre)`

## API Endpoints

### Authentication
- `POST /auth/login` - User login

### Albums
- `GET /albums` - List all albums
- `GET /albums/{album_id}` - Get album details
- `POST /albums` - Create new album review
- `PUT /albums/{album_id}` - Update album review
- `DELETE /albums/{album_id}` - Delete album

### Artists
- `GET /artists` - List all artists
- `GET /artists/{artist_id}` - Get artist details
- `POST /artists` - Create new artist

### Search & Visualization
- `GET /search?q={query}` - Search across albums and artists
- `GET /graph/data` - Get graph data for visualization

## Web Interface Features

### Album Review Entry
- Simple form with album title, artist, year, type
- Rating slider (0.0 to 5.0)
- Large text area for review notes
- Genre and label selection

### Dashboard
- List of all albums
- Search functionality
- Basic filtering (by genre, year, rating)

### Graph Visualization
- Interactive network showing artist influences
- Album connections and similarities
- Simple genre relationships

## Docker Setup

### docker-compose.yml
```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15-community
    container_name: music-graph-neo4j
    environment:
      NEO4J_AUTH: neo4j/your-password-here
      NEO4J_PLUGINS: '["apoc"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - ./neo4j/data:/data
      - ./neo4j/logs:/logs
    restart: unless-stopped

  api:
    build: ./api
    container_name: music-graph-api
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: your-password-here
    ports:
      - "8000:8000"
    depends_on:
      - neo4j
    restart: unless-stopped

  web:
    build: ./web
    container_name: music-graph-web
    ports:
      - "3000:80"
    depends_on:
      - api
    restart: unless-stopped
```

## Implementation Phases

### Phase 1: Core Infrastructure
- [ ] Set up Neo4j with basic schema
- [ ] Create FastAPI project with basic structure
- [ ] Implement CRUD operations for Albums and Artists
- [ ] Set up Docker environment
- [ ] Basic authentication

### Phase 2: Web Interface
- [ ] Create simple web interface for album entry
- [ ] Implement album review form (title, artist, year, type, rating, notes)
- [ ] Add basic search functionality
- [ ] Album listing and detail views

### Phase 3: Graph Features
- [ ] Implement relationship tracking (influences, genres, labels)
- [ ] Add graph visualization using a JavaScript library
- [ ] Create simple graph queries for connected data

### Phase 4: Data Enhancement
- [ ] Optional RateYourMusic/AOTY integration
- [ ] Batch import tools for existing data
- [ ] Export functionality

## Key Implementation Notes

### Core Functionality Focus
- Simple album review entry with plain text notes
- Rating system: 0.0 to 5.0 in 0.1 increments
- Basic relationship tracking between artists and albums
- Graph visualization to see connections and patterns

### Desktop-First Design
- No mobile-specific features needed
- Focus on desktop usability
- Simple, clean web interface

### Data Model Flexibility
- Contributor instead of Producer for broader role coverage
- Album types: LP, EP, Single, Live, Compilation
- Keep schema simple and focused

---

## Next Steps

1. **Initialize project** with basic FastAPI structure
2. **Set up Neo4j** with schema creation scripts
3. **Build core API endpoints** for albums and artists
4. **Create simple web interface** for data entry
5. **Add graph visualization** for exploring relationships