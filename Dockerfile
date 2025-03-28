# Use an official Python 3.11 slim runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# PYTHONUNBUFFERED ensures print statements are sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi.py \
    PORT=5000 \
    # --- Secrets & Configuration ---
    # Provide these via -e or a .env file during docker run
    # GEMINI_API_KEY is required for OCR functionality [cite: PollPulse (2)/PollPulse/utils.py]
    GEMINI_API_KEY="" \
    # SESSION_SECRET defaults if not provided [cite: PollPulse (2)/PollPulse/app.py]
    SESSION_SECRET="a-secure-production-secret-key" \
    # Store the database in a persistent volume mounted at /data
    DATABASE_URL="sqlite:////data/polls.db" \
    # Set Flask environment to production [cite: PollPulse (2)/PollPulse/app.py]
    FLASK_ENV="production"

# Set the working directory in the container
WORKDIR /app

# --- Install Dependencies ---
# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy Application Code ---
# Copy the rest of the application source code into the container
COPY . .

# --- Create Directories & Set Permissions ---
# Create directories for the SQLite database and image uploads
# Ensure the application user ('nobody' in this case) can write to them
RUN mkdir /data static/uploads && chown -R nobody:nogroup /data static/uploads

# Switch to a non-root user for security
USER nobody

# --- Expose Port ---
# Make port 5000 available to the host
EXPOSE 5000

# --- Run the Application ---
# Use Gunicorn with eventlet worker for SocketIO compatibility [cite: PollPulse (2)/PollPulse/run.sh, PollPulse (2)/PollPulse/wsgi.py]
# Bind to 0.0.0.0 to accept connections from any IP
CMD ["gunicorn", "--worker-class", "eventlet", "--workers", "1", "--bind", "0.0.0.0:5000", "wsgi:application"]
