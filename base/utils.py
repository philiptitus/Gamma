# import cv2
# from deepface import DeepFace
# import logging
# from concurrent.futures import ThreadPoolExecutor

# logger = logging.getLogger(__name__)

# def analyze_frame(frame):
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False, detector_backend='mtcnn')
#     return results

# def analyze_video(temp_file_path):
#     cap = cv2.VideoCapture(temp_file_path)
#     frame_skip = 20  # Increase frame skip interval
#     resize_factor = 0.5

#     total_frames = 0
#     calm_frames = 0
#     emotion_counts = {}
#     frame_count = 0

#     with ThreadPoolExecutor(max_workers=4) as executor:  # Use multi-threading
#         futures = []

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             frame_count += 1
#             if frame_count % frame_skip != 0:
#                 continue

#             frame = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
#             futures.append(executor.submit(analyze_frame, frame))

#         for future in futures:
#             results = future.result()
#             for result in results:
#                 dominant_emotion = result['dominant_emotion']
#                 total_frames += 1
#                 if dominant_emotion in ['neutral', 'happy']:
#                     calm_frames += 1

#                 emotion_counts.setdefault(dominant_emotion, 0)
#                 emotion_counts[dominant_emotion] += 1

#     cap.release()
#     cv2.destroyAllWindows()

#     if total_frames == 0:
#         return None

#     calm_percentage = (calm_frames / total_frames) * 100
#     most_dominant_emotion = max(emotion_counts, key=emotion_counts.get)

#     return {
#         "dominant_emotion": most_dominant_emotion,
#         "calm_percentage": calm_percentage,
#         "emotion_counts": emotion_counts,
#     }



import cv2
from deepface import DeepFace
import logging
from concurrent.futures import ThreadPoolExecutor
import tensorflow as tf

logger = logging.getLogger(__name__)

# TensorFlow memory growth configuration
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logger.info("Set memory growth for TensorFlow")
    except RuntimeError as e:
        logger.error(f"Error setting memory growth: {e}")

def analyze_frame(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False, detector_backend='mtcnn')
    return results

def analyze_video(temp_file_path):
    cap = cv2.VideoCapture(temp_file_path)
    frame_skip = 20  # Increase frame skip interval
    resize_factor = 0.5

    total_frames = 0
    calm_frames = 0
    emotion_counts = {}
    frame_count = 0

    with ThreadPoolExecutor(max_workers=4) as executor:  # Use multi-threading
        futures = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            frame = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
            futures.append(executor.submit(analyze_frame, frame))

        for future in futures:
            results = future.result()
            for result in results:
                dominant_emotion = result['dominant_emotion']
                total_frames += 1
                if dominant_emotion in ['neutral', 'happy']:
                    calm_frames += 1

                emotion_counts.setdefault(dominant_emotion, 0)
                emotion_counts[dominant_emotion] += 1

    cap.release()
    cv2.destroyAllWindows()

    if total_frames == 0:
        return None

    calm_percentage = (calm_frames / total_frames) * 100
    most_dominant_emotion = max(emotion_counts, key=emotion_counts.get)

    return {
        "dominant_emotion": most_dominant_emotion,
        "calm_percentage": calm_percentage,
        "emotion_counts": emotion_counts,
    }


from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.utils.html import strip_tags
from django.conf import settings



def send_normal_email(data):
    # Load and render the template with context
    template = Template(data['email_body'])
    context = Context(data.get('context', {}))
    html_content = template.render(context)
    text_content = strip_tags(html_content)  # Fallback text content

    # Create email message
    email = EmailMultiAlternatives(
        subject=data['email_subject'],
        body=html_content,  # Plain text content for email clients that don't support HTML
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']],
    )
    email.attach_alternative(html_content, "text/html")  # Attach the HTML version

    # Send email
    email.send()


