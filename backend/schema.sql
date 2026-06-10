-- SUPPRIMER LES TABLES ---
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS post_availabilities;
DROP TABLE IF EXISTS mentorship_posts;
DROP TABLE IF EXISTS user_availabilities;
DROP TABLE IF EXISTS user_skills;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS users;

-- ── TABLE: users ─────────────────────────────────────────────
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  phone_number VARCHAR(20) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  profile_photo VARCHAR(255), -- URL, NULL si pas de photo
  field_of_study VARCHAR(50) NOT NULL, -- IA, IM, GL, SE&IoT, SI
  level VARCHAR(20) NOT NULL, -- L1, L2, L3, M1, M2
  bio TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── TABLE: skills ────────────────────────────────────────────
CREATE TABLE skills (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── TABLE: user_skills ───────────────────────────────────────
-- Compétences et lacunes d'un utilisateur (many-to-many avec attribut)
CREATE TABLE user_skills (
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  skill_id INT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  proficiency VARCHAR(10) NOT NULL CHECK (proficiency IN ('strong', 'weak')),
  PRIMARY KEY (user_id, skill_id)
  -- 'strong' = point fort (peut enseigner)
  -- 'weak' = lacune (a besoin d'aide)
);

-- ── TABLE: user_availabilities ───────────────────────────────
-- Disponibilités horaires habituelles de l'utilisateur
CREATE TABLE user_availabilities (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  day_of_week VARCHAR(10) NOT NULL CHECK (day_of_week IN (
    'Monday','Tuesday','Wednesday','Thursday',
    'Friday','Saturday','Sunday'
  )),
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  CONSTRAINT chk_user_avail_time CHECK (start_time < end_time)
);

-- ── TABLE: mentorship_posts ──────────────────────────────────
-- Offres et demandes de mentorat publiées par les utilisateurs
CREATE TABLE mentorship_posts (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(10) NOT NULL CHECK (type IN ('offer', 'request')),
  skill_id INT NOT NULL REFERENCES skills(id),
  mode VARCHAR(10) NOT NULL CHECK (mode IN ('online', 'offline', 'both')),
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE, -- FALSE pour archiver sans supprimer
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── TABLE: post_availabilities ───────────────────────────────
-- Disponibilités horaires spécifiques à un post
CREATE TABLE post_availabilities (
  id SERIAL PRIMARY KEY,
  post_id INT NOT NULL REFERENCES mentorship_posts(id) ON DELETE CASCADE,
  day_of_week VARCHAR(10) NOT NULL CHECK (day_of_week IN (
    'Monday','Tuesday','Wednesday','Thursday',
    'Friday','Saturday','Sunday'
  )),
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  CONSTRAINT chk_post_avail_time CHECK (start_time < end_time)
);

-- ── TABLE: matches ───────────────────────────────────────────
-- Correspondances mentor ↔ mentoré calculées par l'algorithme
CREATE TABLE matches (
  id SERIAL PRIMARY KEY,
  mentor_id INT NOT NULL REFERENCES users(id),
  mentee_id INT NOT NULL REFERENCES users(id),
  offer_post_id INT REFERENCES mentorship_posts(id),
  request_post_id INT REFERENCES mentorship_posts(id),
  skill_id INT REFERENCES skills(id),
  score DECIMAL(5,2) NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  CHECK (status IN ('pending', 'accepted', 'rejected')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT chk_mentor_mentee_diff CHECK (mentor_id != mentee_id)
);

-- ── TABLE: conversations ─────────────────────────────────────
-- Une conversation est créée pour chaque match accepté (1:1 avec matches)
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  match_id INT NOT NULL UNIQUE REFERENCES matches(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── TABLE: messages ──────────────────────────────────────────
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  conversation_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  sender_id INT NOT NULL REFERENCES users(id),
  content TEXT NOT NULL,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── INDEX (pour meilleures performances des requêtes) ────────
CREATE INDEX idx_user_skills_user ON user_skills(user_id);
CREATE INDEX idx_user_skills_skill ON user_skills(skill_id);
CREATE INDEX idx_avail_user ON user_availabilities(user_id);
CREATE INDEX idx_posts_user ON mentorship_posts(user_id);
CREATE INDEX idx_posts_skill ON mentorship_posts(skill_id);
CREATE INDEX idx_posts_active ON mentorship_posts(is_active);
CREATE INDEX idx_matches_mentor ON matches(mentor_id);
CREATE INDEX idx_matches_mentee ON matches(mentee_id);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_messages_conv ON messages(conversation_id);
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_created ON messages(created_at);