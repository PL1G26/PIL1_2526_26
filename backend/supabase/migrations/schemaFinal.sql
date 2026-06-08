CREATE TABLE IF NOT EXISTS users
(
  id SERIAL PRIMARY KEY ,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  phone_number VARCHAR(20) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  profile_photo VARCHAR(255),
  field_of_study VARCHAR(50) NOT NULL,
  level VARCHAR(20) NOT NULL,
  bio TEXT,
  created_at timestamp,
  updated_at TIMESTAMP 
);

CREATE TABLE IF NOT EXISTS skills
(
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS  user_skills   
(
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  skill_id INT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  proficiency VARCHAR(10) NOT NULL CHECK (proficiency IN ('strong', 'weak')),
  PRIMARY KEY (user_id, skill_id)
);

CREATE TABLE IF NOT EXISTS user_availabilities 
(
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) on delete cascade ,
  day_of_week VARCHAR(10) NOT NULL CHECK (day_of_week IN('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')),
  start_time TIME NOT NULL ,
  end_time TIME NOT NULL,
  CONSTRAINT chk_user_time_order CHECK (end_time > start_time)
);

CREATE TABLE IF NOT EXISTS mentorship_posts 
(
  id SERIAL PRIMARY KEY,
  user_id INT  NOT NULL REFERENCES users(id) ON DELETE CASCADE ,
  type VARCHAR(10) NOT NULL CHECK(type IN('offer','request')),
  skill_id INT NOT NULL REFERENCES skills(id),
  mode VARCHAR(10) NOT NULL CHECK (mode IN('EN LIGNE','PRESENTIEL')),
  description TEXT ,
  is_active BOOLEAN DEFAULT TRUE ,
  created_at TIMESTAMP  NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()

);

CREATE TABLE IF NOT EXISTS post_availabilities
(
  id SERIAL PRIMARY KEY,
  post_id INT  NOT NULL REFERENCES mentorship_posts(id),
  day_of_week VARCHAR(10) NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL 
);

CREATE TABLE IF NOT EXISTS matches
(
  id SERIAL PRIMARY KEY,
  mentor_id INT NOT NULL REFERENCES users(id),
  mentee_id INT NOT NULL REFERENCES users(id),
  offer_post_id INT  REFERENCES mentorship_post(id),
  request_post_id INT REFERENCES mentorship_post(id),
  skill_id INT REFERENCES skills(id),
  score DECIMAL(5,2) NOT NULL DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'pending'CHECK (status IN('pending', 'accepted', 'rejected')),
  created_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT chk_mentor_mentee_diff CHECK (mentor_id <> mentee_id)

);

CREATE TABLE IF NOT EXISTS conversations
( 
  id SERIAL PRIMARY KEY,
  match_id INT NOT NULL UNIQUE REFERENCES matches(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages
(
  id SERIAL PRIMARY KEY,
  conversation_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  sender_id INT NOT NULL REFERENCES users(id),
  content TEXT NOT NULL,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

