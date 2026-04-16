-- CineMetrics Database Schema
-- Phase 2: Full DDL for CineMetrics
-- 13 tables in dependency order

DROP DATABASE IF EXISTS CineMetrics;
CREATE DATABASE CineMetrics;
USE CineMetrics;

-- ============================================================
-- Drop tables in reverse dependency order (if they exist)
-- ============================================================
DROP TABLE IF EXISTS AdminLog;
DROP TABLE IF EXISTS ReviewFlag;
DROP TABLE IF EXISTS RecommendationClick;
DROP TABLE IF EXISTS Recommendation;
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS Rating;
DROP TABLE IF EXISTS WatchlistItem;
DROP TABLE IF EXISTS Watchlist;
DROP TABLE IF EXISTS WatchHistory;
DROP TABLE IF EXISTS MovieGenre;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Movie;
DROP TABLE IF EXISTS `User`;

-- ============================================================
-- Table 1: User
-- Stores all platform users (casual viewers, enthusiasts,
-- analysts, and admins).
-- ============================================================
CREATE TABLE `User` (
    user_id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('casual', 'enthusiast', 'admin', 'analyst') NOT NULL DEFAULT 'casual',
    join_date DATE NOT NULL,
    status ENUM('active', 'inactive', 'banned') NOT NULL DEFAULT 'active',
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_user_email (email),
    UNIQUE KEY uq_user_username (username)
);

-- ============================================================
-- Table 2: Movie
-- Core movie catalog with metadata and aggregate rating.
-- ============================================================
CREATE TABLE Movie (
    movie_id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    release_year INT NOT NULL,
    runtime_minutes INT,
    synopsis TEXT,
    country_of_origin VARCHAR(100),
    language VARCHAR(50),
    average_rating DECIMAL(3, 2) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('active', 'removed', 'flagged') NOT NULL DEFAULT 'active',
    PRIMARY KEY (movie_id)
);

-- ============================================================
-- Table 3: Genre
-- Lookup table for movie genres.
-- ============================================================
CREATE TABLE Genre (
    genre_id INT NOT NULL AUTO_INCREMENT,
    genre_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (genre_id),
    UNIQUE KEY uq_genre_name (genre_name)
);

-- ============================================================
-- Table 4: MovieGenre (bridge table)
-- Many-to-many relationship between Movie and Genre.
-- ============================================================
CREATE TABLE MovieGenre (
    movie_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (movie_id, genre_id),
    CONSTRAINT fk_moviegenre_movie FOREIGN KEY (movie_id) REFERENCES Movie (movie_id) ON DELETE CASCADE,
    CONSTRAINT fk_moviegenre_genre FOREIGN KEY (genre_id) REFERENCES Genre (genre_id) ON DELETE CASCADE
);

-- ============================================================
-- Table 5: WatchHistory
-- Tracks which movies a user has watched, including completion
-- status and rewatch count.
-- ============================================================
CREATE TABLE WatchHistory (
    history_id INT NOT NULL AUTO_INCREMENT,
    watched_date DATE NOT NULL,
    completion_status ENUM('completed', 'in_progress', 'abandoned') NOT NULL DEFAULT 'in_progress',
    rewatch_count INT NOT NULL DEFAULT 0,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    PRIMARY KEY (history_id),
    CONSTRAINT fk_watchhistory_user FOREIGN KEY (user_id) REFERENCES `User` (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_watchhistory_movie FOREIGN KEY (movie_id) REFERENCES Movie (movie_id) ON DELETE CASCADE
);

-- ============================================================
-- Table 6: Watchlist
-- Named watchlists owned by a user.
-- ============================================================
CREATE TABLE Watchlist (
    watchlist_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    PRIMARY KEY (watchlist_id),
    CONSTRAINT fk_watchlist_user FOREIGN KEY (user_id) REFERENCES `User` (user_id) ON DELETE CASCADE
);

-- ============================================================
-- Table 7: WatchlistItem
-- Individual movies added to a watchlist.
-- ============================================================
CREATE TABLE WatchlistItem (
    watchlist_item_id INT NOT NULL AUTO_INCREMENT,
    added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    watchlist_id INT NOT NULL,
    movie_id INT NOT NULL,
    PRIMARY KEY (watchlist_item_id),
    CONSTRAINT fk_watchlistitem_watchlist FOREIGN KEY (watchlist_id) REFERENCES Watchlist (watchlist_id) ON DELETE CASCADE,
    CONSTRAINT fk_watchlistitem_movie FOREIGN KEY (movie_id) REFERENCES Movie (movie_id) ON DELETE CASCADE
);

-- ============================================================
-- Table 8: Rating
-- Numeric ratings (0.0 - 10.0) that users assign to movies.
-- ============================================================
CREATE TABLE Rating (
    rating_id INT NOT NULL AUTO_INCREMENT,
    rating_value DECIMAL(3, 1) NOT NULL,
    rating_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    PRIMARY KEY (rating_id),
    CONSTRAINT chk_rating_value CHECK (rating_value >= 0.0 AND rating_value <= 10.0),
    CONSTRAINT fk_rating_user FOREIGN KEY (user_id) REFERENCES `User` (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_rating_movie FOREIGN KEY (movie_id) REFERENCES Movie (movie_id) ON DELETE CASCADE
);

-- ============================================================
-- Table 9: Review
-- Written reviews tied to a user and movie, with moderation
-- support and soft-delete capability.
-- ============================================================
CREATE TABLE Review (
    review_id INT NOT NULL AUTO_INCREMENT,
    review_title VARCHAR(255) NOT NULL,
    review_body TEXT NOT NULL,
    review_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    moderation_status ENUM('approved', 'pending', 'rejected') NOT NULL DEFAULT 'pending',
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    PRIMARY KEY (review_id),
    CONSTRAINT fk_review_user FOREIGN KEY (user_id) REFERENCES `User` (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_review_movie FOREIGN KEY (movie_id) REFERENCES Movie (movie_id) ON DELETE CASCADE
);

-- ============================================================
-- Table 10: Recommendation
-- System-generated movie recommendations for users, with a
-- score and human-readable reason.
-- ============================================================
CREATE TABLE Recommendation (
    recommendation_id INT NOT NULL AUTO_INCREMENT,
    reason TEXT,
    recommendation_score DECIMAL(5, 2),
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    PRIMARY KEY (recommendation_id),
    CONSTRAINT fk_recommendation_user FOREIGN KEY (user_id) REFERENCES `User` (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_recommendation_movie FOREIGN KEY (movie_id) REFERENCES Movie (movie_id) ON DELETE CASCADE
);

-- ============================================================
-- Table 11: RecommendationClick
-- Tracks when a user clicks on a recommendation (engagement
-- analytics).
-- ============================================================
CREATE TABLE RecommendationClick (
    click_id INT NOT NULL AUTO_INCREMENT,
    clicked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recommendation_id INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (click_id),
    CONSTRAINT fk_recclick_recommendation FOREIGN KEY (recommendation_id) REFERENCES Recommendation (recommendation_id) ON DELETE CASCADE,
    CONSTRAINT fk_recclick_user FOREIGN KEY (user_id) REFERENCES `User` (user_id) ON DELETE CASCADE
);

-- ============================================================
-- Table 12: ReviewFlag
-- Allows users to flag reviews for moderation. Uses RESTRICT
-- on the flagging user to preserve audit trail.
-- ============================================================
CREATE TABLE ReviewFlag (
    flag_id INT NOT NULL AUTO_INCREMENT,
    flag_reason TEXT,
    flag_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    flag_status ENUM('pending', 'reviewed', 'dismissed') NOT NULL DEFAULT 'pending',
    review_id INT NOT NULL,
    flagged_by_user_id INT NOT NULL,
    PRIMARY KEY (flag_id),
    CONSTRAINT fk_reviewflag_review FOREIGN KEY (review_id) REFERENCES Review (review_id) ON DELETE CASCADE,
    CONSTRAINT fk_reviewflag_user FOREIGN KEY (flagged_by_user_id) REFERENCES `User` (user_id) ON DELETE RESTRICT
);

-- ============================================================
-- Table 13: AdminLog
-- Audit log for admin actions. Uses RESTRICT on the admin
-- user to prevent deletion of admins with log history.
-- ============================================================
CREATE TABLE AdminLog (
    log_id INT NOT NULL AUTO_INCREMENT,
    action_type VARCHAR(100) NOT NULL,
    target_table VARCHAR(100),
    target_id INT,
    action_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    admin_user_id INT NOT NULL,
    PRIMARY KEY (log_id),
    CONSTRAINT fk_adminlog_user FOREIGN KEY (admin_user_id) REFERENCES `User` (user_id) ON DELETE RESTRICT
);
