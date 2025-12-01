# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Readiego** is a book recommendation system that uses graph-based collaborative filtering with user authentication. It consists of:
- **Backend**: Flask API using NetworkX for bipartite graph-based recommendations
- **Frontend**: React + Vite SPA with React Router and Tailwind CSS
- **Database**: PostgreSQL storing Book-Crossing dataset (books, users, ratings) + app users/ratings
- **Data Source**: Kaggle Book-Crossing dataset (~271K books, ~279K users, ~1.1M ratings)

The system builds a bipartite graph connecting users and books through ratings, then uses:
- **Collaborative Filtering**: Recommends books based on similar users (Jaccard or Cosine similarity)
- **Item-Based Filtering**: Recommends similar books based on shared readers
- **Hybrid Recommender**: Combines collaborative + content-based (author, year) with quality filters

## Development Commands

### Backend Setup & Running

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

# Configure database credentials in .env (copy from .env.example)
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=readiego
# DB_USER=postgres
# DB_PASSWORD=your_password

python app.py  # Runs on http://localhost:5000
```

**Sample vs Full Dataset**: By default, the system loads 10,000 ratings for faster development. To use the full dataset, modify [app.py:208](backend/app.py#L208):
```python
initialize_system(use_sample=False)  # Use all ~1.1M ratings
```

### Frontend Setup & Running

```bash
cd frontend
npm install
npm run dev      # Development server (http://localhost:5173)
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

### Database Setup

**Initial Migration from CSV** (one-time):
```bash
# 1. Create PostgreSQL database
psql -U postgres
CREATE DATABASE readiego;
\q

# 2. Run migration script (requires CSV files in data/ directory)
cd database
python migrate_csv_to_db.py
```

**Schema Management**:
```bash
# Apply schema (creates tables, views, indexes)
psql -U postgres -d readiego -f database/schema.sql

# Verify data
psql -U postgres -d readiego
SELECT COUNT(*) FROM books;     # ~271,360
SELECT COUNT(*) FROM users;     # ~278,858
SELECT COUNT(*) FROM ratings;   # ~1,149,780
```

## Architecture

### Backend Structure

**Core Components**:

1. **GraphEngine** ([graph_engine.py](backend/graph_engine.py))
   - Manages bipartite graph using NetworkX
   - Nodes: Users (bipartite=0) and Books (bipartite=1)
   - Edges: Ratings (weighted edges between users and books)
   - Key methods:
     - `add_rating(user_id, book_id, rating)`: Add user-book edge
     - `get_user_books(user_id)`: Get all books rated by user
     - `get_book_users(book_id)`: Get all users who rated a book
     - `get_graph_stats()`: Returns user/book counts, edge count, graph density

2. **BookRecommender** ([recommender.py](backend/recommender.py))
   - Basic recommendation algorithms using Jaccard similarity
   - **Collaborative filtering**: Finds similar users based on shared books
   - **Item-based filtering**: Finds similar books based on shared readers
   - Key methods:
     - `recommend_collaborative(user_id, top_n)`: User-based recommendations
     - `recommend_by_book(book_id, top_n)`: Similar books
     - `_find_similar_users()`: Finds top N similar users (Jaccard index)
     - `_calculate_book_similarity()`: Calculates book similarity (Jaccard index)

3. **HybridRecommender** ([hybrid_recommender.py](backend/hybrid_recommender.py))
   - Advanced hybrid system combining multiple approaches
   - Uses **cosine similarity** (more precise than Jaccard for weighted ratings)
   - **Collaborative filtering (60% weight)**: Similar users based on rating vectors
   - **Content-based filtering (40% weight)**: Similar books by author, year
   - **Quality filter**: Only recommends books with avg rating ≥ 6.0
   - **Diversity filter**: Max 2 books per author in recommendations
   - Fallback: Popular books for new users without ratings

4. **DataLoader** ([data_loader.py](backend/data_loader.py))
   - Loads data from PostgreSQL (not CSV)
   - Filters ratings: Only explicit ratings (rating > 0) via `explicit_ratings` view
   - Provides metadata lookup: `get_book_info(isbn)`, `get_user_info(user_id)`
   - Supports sampling: `load_all(sample_size=10000)` for development

5. **DatabaseConnection** ([database.py](backend/database.py))
   - Handles PostgreSQL connections using psycopg2
   - Reads credentials from `.env` file (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
   - Supports both dict cursors (returns rows as dicts) and regular cursors
   - Context manager support: `with DatabaseConnection() as db:`

6. **Authentication System** ([auth.py](backend/auth.py), [app_routes.py](backend/app_routes.py))
   - JWT-based authentication with bcrypt password hashing
   - Separate `app_users` table from Book-Crossing dataset users
   - `@token_required` decorator for protected routes
   - Token valid for 7 days
   - Test users: juan, maria, carlos (password: password123)

**Database Schema**:

Two types of users and ratings:
- **Book-Crossing Dataset** (`users`, `ratings`): Read-only historical data for graph
- **App Users** (`app_users`, `app_user_ratings`): New users created via registration

```sql
-- Book-Crossing data (read-only, used for graph recommendations)
books (isbn PK, title, author, year_of_publication, publisher, image_url_*)
users (user_id PK, location, age)
ratings (user_id FK, isbn FK, rating 0-10, unique(user_id, isbn))
explicit_ratings VIEW (ratings WHERE rating > 0)

-- App users (created via registration, can rate books)
app_users (id PK, email unique, username unique, password_hash, full_name, is_active, last_login)
app_user_ratings (app_user_id FK, isbn FK, rating 1-10, review, unique(app_user_id, isbn))
```

**API Endpoints**:

*Authentication*:
- `POST /api/auth/register` - Register new user (email, username, password, full_name)
- `POST /api/auth/login` - Login (returns JWT token)
- `GET /api/auth/me` - Get current user info (requires auth)

*Book Catalog*:
- `GET /api/catalog/books?page=1&limit=20&search=query` - Paginated book catalog with search

*User Ratings*:
- `GET /api/ratings/my-ratings` - Get authenticated user's ratings (requires auth)
- `POST /api/ratings/rate` - Rate a book (isbn, rating 1-10, review) (requires auth)
- `DELETE /api/ratings/delete/<isbn>` - Delete rating (requires auth)

*Recommendations*:
- `GET /api/recommendations/for-me?top_n=10` - Personalized recommendations for authenticated user
  - Temporarily adds user's ratings to graph
  - Generates recommendations using collaborative filtering
  - Cleans up temporary user from graph

*Legacy/System Endpoints*:
- `GET /api/health` - System stats (users, books, ratings, density)
- `GET /api/recommend/user/<user_id>?top_n=10` - User recommendations (Book-Crossing users)
- `GET /api/recommend/book/<isbn>?top_n=10` - Similar books
- `GET /api/book/<isbn>` - Book metadata
- `GET /api/user/<user_id>` - User metadata (Book-Crossing users)
- `GET /api/user/<user_id>/books` - Books rated by user
- `GET /api/debug/sample-users` - Get sample user IDs for testing

### Frontend Structure

**React Architecture**:
- React 19 + React Router v7 + Tailwind CSS
- Context API for state management (AuthContext)
- Protected routes using PrivateRoute wrapper component

**Pages**:
- [Login.jsx](frontend/src/components/Login.jsx) - Login form
- [Register.jsx](frontend/src/components/Register.jsx) - Registration form
- [Dashboard.jsx](frontend/src/pages/Dashboard.jsx) - Personalized recommendations for logged-in user
- [Catalog.jsx](frontend/src/pages/Catalog.jsx) - Browse and search books, rate books
- [MyRatings.jsx](frontend/src/pages/MyRatings.jsx) - View and manage user's ratings

**Key Components**:
- [Navbar.jsx](frontend/src/components/Navbar.jsx) - Navigation with login/logout
- [RatingStars.jsx](frontend/src/components/RatingStars.jsx) - Star rating component (1-10 scale)

**State Management**:
- [AuthContext.jsx](frontend/src/context/AuthContext.jsx):
  - Manages authentication state (user, token, isAuthenticated)
  - Stores JWT token in localStorage
  - Adds Authorization header to API requests
  - Methods: `login(email_or_username, password)`, `register(...)`, `logout()`

**API Integration**:
- Axios configured with base URL: `http://localhost:5000/api`
- JWT token automatically included in Authorization header when authenticated
- API calls made through fetch/axios with proper error handling

## Data Requirements

The system uses PostgreSQL instead of CSV files. Initial setup requires CSV files from [Book-Crossing Dataset](https://www.kaggle.com/datasets/ruchi798/bookcrossing-dataset) to be migrated:
- **Books.csv**: ISBN, Title, Author, Year, Publisher, Image URLs (~271K books)
- **Ratings.csv**: User_ID, ISBN, Rating (0-10 scale) (~1.1M ratings)
- **Users.csv**: User_ID, Location, Age (~279K users)

After migration, CSV files are no longer needed. See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details.

## Important Implementation Details

### Graph-Based Recommendation Flow

1. **Data Loading**: DataLoader fetches from PostgreSQL `explicit_ratings` view (rating > 0)
2. **Graph Construction**: GraphEngine builds bipartite graph with user-book edges weighted by ratings
3. **Similarity Calculation**:
   - **Jaccard** (BookRecommender): Set-based similarity (presence/absence of books)
   - **Cosine** (HybridRecommender): Vector-based similarity (considers rating magnitudes)
4. **Recommendation Generation**:
   - Find top N similar users (default 10 for Jaccard, 50 for Cosine)
   - Aggregate their book ratings weighted by user similarity
   - Return top N unread books with highest scores

### Authentication Flow

1. User registers → password hashed with bcrypt → stored in `app_users`
2. User logs in → credentials verified → JWT token generated (7-day expiry)
3. Frontend stores token in localStorage
4. Protected API calls include: `Authorization: Bearer <token>`
5. Backend validates token via `@token_required` decorator
6. For recommendations: app user's ratings temporarily added to graph, then removed

### Hybrid Recommender Details

- **Why Hybrid?**: Combines strengths of collaborative (user similarity) + content (book features)
- **Cosine vs Jaccard**: Cosine considers rating magnitudes (user rated 10 vs 5), Jaccard only book presence
- **Quality Filter**: Prevents recommending poorly-rated books (avg < 6.0)
- **Diversity Filter**: Prevents recommending many books from same author (max 2)
- **Cold Start**: New users without ratings get popular books (high avg rating + many ratings)

### Performance Considerations

- **Sample Mode**: Default `sample_size=10000` loads ~10K ratings for fast startup (~2-5 seconds)
- **Full Dataset**: 1.1M ratings takes significantly longer to load and compute (~30-60 seconds)
- **Graph Density**: Very sparse (~0.0001) due to large user/book space
- **Database Indexing**: Indexes on `user_id`, `isbn`, `rating` columns for fast queries
- **Pagination**: Catalog endpoint uses LIMIT/OFFSET with `COUNT(*) OVER()` for total count

### Cross-Origin Setup

Backend uses Flask-CORS to allow requests from frontend development server (localhost:5173).

## Common Gotchas

- **Two User Systems**: Book-Crossing `users` (historical data) vs `app_users` (new registrations)
- **Rating Scales**: Book-Crossing uses 0-10 (0=implicit, excluded), app users use 1-10
- **String IDs**: User IDs and ISBNs stored as strings in graph (convert with `str()`)
- **Sample vs Full**: Remember to switch `use_sample=False` when testing production performance
- **Database Required**: Backend won't start without PostgreSQL connection
- **Environment Variables**: Copy `.env.example` to `.env` and configure database credentials
- **Temp Graph Nodes**: `/api/recommendations/for-me` adds temp user (`app_<id>`), must clean up
- **JWT Secret**: Change `JWT_SECRET_KEY` and `SECRET_KEY` in production
- **Frontend Auth**: Check `isAuthenticated` from AuthContext, redirect to login if needed
- **CORS**: Backend must be running for frontend to work (API calls fail otherwise)
