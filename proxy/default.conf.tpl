upstream app {
    server app:9000;  # Ensure this matches the service name and port in your docker-compose
}

server {
    listen 80;

    location / {
        include uwsgi_params;  # Include the uwsgi_params file
        uwsgi_pass app;        # Pass requests to the uWSGI server
    }
}