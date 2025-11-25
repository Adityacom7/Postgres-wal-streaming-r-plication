FROM postgres:15

# Copy initialization script
COPY init.sql /docker-entrypoint-initdb.d/

# Copy custom pg_hba.conf that will be used
COPY pg_hba.conf /docker-entrypoint-initdb.d/pg_hba.conf

# Copy setup script
COPY setup-master.sh /docker-entrypoint-initdb.d/

# Make script executable
RUN chmod +x /docker-entrypoint-initdb.d/setup-master.sh

# Set environment variables
ENV POSTGRES_DB=scandb
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Expose PostgreSQL port
EXPOSE 5432
