-- PostgreSQL ejecuta este archivo mediante psql al crear PGDATA.
-- La aplicación trabaja con fechas conscientes de zona y persiste en UTC.
SELECT format('ALTER DATABASE %I SET timezone TO %L', current_database(), 'UTC')
\gexec
