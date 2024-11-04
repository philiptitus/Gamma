# Gamma API

Gamma API is a Django-based RESTful API designed to analyze emotions from video files. It utilizes `cv2` and the `DeepFace` library to perform facial emotion detection on video frames. Emotions are analyzed using TensorFlow for efficient GPU-based computation, with the results stored and shared with users via email notifications.

## Core Features

1. **Video Emotion Analysis**: Processes video frames to detect and analyze emotions.
2. **Multi-Threading**: Uses threading to improve performance and handle multiple requests concurrently.
3. **AWS S3 Integration**: Temporarily stores video files in an S3 bucket before analysis.
4. **Email Notifications**: Sends analysis results to users via email.
5. **Token-Based Session Tracking**: Assigns unique tokens for each session to track individual video analysis tasks.

## Technologies Used

### 1. Python Libraries and Frameworks
- **Django**: The web framework that powers Gamma API, enabling efficient handling of HTTP requests and database interactions.
- **Django REST Framework (DRF)**: Used to create the API endpoints for uploading videos and retrieving results.
- **OpenCV (cv2)**: Processes video frames, resizes them, and performs basic pre-processing.
- **DeepFace**: Performs emotion detection on individual frames, analyzing faces with the MTCNN backend.
- **TensorFlow**: Configured to use GPU memory efficiently for accelerated deep learning tasks.
- **Boto3**: AWS SDK for Python, handling interactions with AWS S3 for video storage.

### 2. Multi-Threading and Queue Management
- **ThreadPoolExecutor**: Allows concurrent frame analysis using multiple threads.
- **Threading and Queue**: A worker thread is used to handle video processing tasks in a queue, ensuring efficient task execution.

### 3. Amazon Web Services (AWS)
- **Amazon S3**: Stores video files temporarily, enabling streaming for analysis without relying on local storage.
- **AWS S3 Credentials**: Access to S3 is managed through AWS credentials set in Django's settings file.

### 4. Email Notifications
- **Django Email System**: Sends email reports to users upon analysis completion.
- **HTML Templates**: Custom email templates are used to display results, including dominant emotion and calmness percentage.

## Installation

### Prerequisites
- Python 3.x
- Virtual environment tool (e.g., `venv`)
- AWS account with an S3 bucket
- Django and Django REST Framework
- TensorFlow-compatible GPU (optional but recommended for performance)

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/philiptitus/Gamma-API.git
   cd Gamma-API
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Configure AWS credentials in your Django settings:
     ```python
     AWS_ACCESS_KEY_ID = '<YOUR_AWS_ACCESS_KEY>'
     AWS_SECRET_ACCESS_KEY = '<YOUR_AWS_SECRET_KEY>'
     AWS_STORAGE_BUCKET_NAME = '<YOUR_BUCKET_NAME>'
     AWS_S3_REGION_NAME = '<YOUR_REGION>'
     AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
     ```
   - Set up email credentials for notification delivery:
     ```python
     EMAIL_HOST = 'smtp.your_email_host.com'
     EMAIL_PORT = 587
     EMAIL_HOST_USER = 'your_email@example.com'
     EMAIL_HOST_PASSWORD = 'your_password'
     EMAIL_USE_TLS = True
     ```

5. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Start the Django server**:
   ```bash
   python manage.py runserver
   ```

### API Endpoints

#### Upload and Analyze Video
- **Endpoint**: `/analyze-video/`
- **Method**: POST
- **Description**: Accepts a video file and email, then initiates analysis and returns a token for tracking the session.

**Request Body**:
- `video`: The video file to be analyzed.
- `email`: Email address to send results to.

**Response**:
```json
{
  "token": "<unique_session_token>"
}
```

### Example Usage

1. **Uploading a Video for Analysis**:
   ```bash
   curl -X POST -F "video=@path/to/video.mp4" -F "email=user@example.com" http://localhost:8000/analyze-video/
   ```
   Response:
   ```json
   {
       "token": "123e4567-e89b-12d3-a456-426614174000"
   }
   ```

### Technical Breakdown

1. **Video Analysis Flow**:
   - Videos are uploaded to an S3 bucket.
   - Frames are extracted and resized.
   - Emotion analysis is performed on every 20th frame (configurable).
   - Emotion results are stored and processed, generating a calmness score and dominant emotion.

2. **Session Tracking**:
   - Each video analysis session is assigned a unique token, stored in the database with the analysis results.

3. **Multi-Threaded Emotion Analysis**:
   - Uses `ThreadPoolExecutor` for concurrent frame analysis.
   - Thread queue ensures stable task processing, improving performance under high loads.

4. **Email Notification**:
   - Results are formatted and sent as HTML emails, including the dominant emotion and calmness score.
   - Email templates are stored in the Django project for easy customization.

## Contributing

Contributions are welcome! If you'd like to improve the functionality or add new features, please open an issue or submit a pull request.

## License

This project is open-source and licensed under the MIT License.

---

&copy; 2024 Philip Titus
