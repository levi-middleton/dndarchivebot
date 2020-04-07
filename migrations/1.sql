-- Create main submission table
CREATE TABLE IF NOT EXISTS submissions
	(id text NOT NULL,
	 permalink text NOT NULL,
	 title text NOT NULL,
	 tags text);
