-- AI Social Media Platform - MySQL 8 schema
-- Mirrors the core database design documented in PROJECT_GUIDE.md.
-- The richer SQLite prototype in api/database_manager.py remains available
-- for self-contained demos; this file is the reproducible MySQL setup path.

CREATE DATABASE IF NOT EXISTS ai_social_media
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE ai_social_media;

CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    caption TEXT NOT NULL,
    hashtags TEXT,
    image_url VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    engagement_score FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_posts_platform (platform),
    INDEX idx_posts_status (status),
    INDEX idx_posts_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    scheduled_time DATETIME NOT NULL,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_schedules_post
        FOREIGN KEY (post_id) REFERENCES posts(id)
        ON DELETE CASCADE,
    INDEX idx_schedules_due (status, scheduled_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    likes INT NOT NULL DEFAULT 0,
    reach INT NOT NULL DEFAULT 0,
    comments INT NOT NULL DEFAULT 0,
    shares INT NOT NULL DEFAULT 0,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_analytics_post
        FOREIGN KEY (post_id) REFERENCES posts(id)
        ON DELETE CASCADE,
    INDEX idx_analytics_post_time (post_id, fetched_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS trends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    score FLOAT NOT NULL DEFAULT 0,
    platform VARCHAR(50) NOT NULL DEFAULT 'general',
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_trends_platform_time (platform, recorded_at),
    INDEX idx_trends_keyword (keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
