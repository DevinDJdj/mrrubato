CREATE TABLE inquiries (
  query TEXT NOT NULL, -- query in
  response TEXT NOT NULL, -- response out
  context TEXT NOT NULL, -- context if any
  prompt TEXT NOT NULL, --prompt if any
  userid TEXT NOT NULL, -- this comes from the Google Oauth
  confidence FLOAT DEFAULT 0, -- how certain are we from the language engine?  
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  --perhaps some more.  


);