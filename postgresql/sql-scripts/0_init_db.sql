DROP DATABASE IF EXISTS memechose;
DROP ROLE IF EXISTS memeuser;

CREATE DATABASE memechose;
CREATE ROLE memeuser WITH LOGIN;
ALTER USER memeuser WITH PASSWORD 'memepass';
GRANT ALL ON DATABASE memechose TO memeuser;
ALTER DATABASE memechose OWNER TO memeuser;

ALTER ROLE memeuser CREATEDB;
-- GRANT ALL ON test.* TO memeuser;
