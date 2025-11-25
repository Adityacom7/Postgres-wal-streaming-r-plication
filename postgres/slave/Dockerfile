FROM postgres:15

# Copy the standby setup script to the root of the container
COPY setup-standby.sh /setup-standby.sh

# Make sure the script is executable
RUN chmod +x /setup-standby.sh
RUN chown -R 777 /var/lib/postgresql/data
RUN chmod 777 /var/lib/postgresql/data


# Pass through required environment variables (replication configuration)
ENV POSTGRES_DB=scandb
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV MASTER_HOST=postgres-master
ENV MASTER_PORT=5432
ENV REPLICATION_USER=replicator
ENV REPLICATION_PASSWORD=replicapass

# Use the standby setup script as the entrypoint
ENTRYPOINT ["/setup-standby.sh"]
