from app.local_memory.classifier import get_classifier
import sys

try:
    print("Initializing classifier...")
    clf = get_classifier()
    
    text_high = "My favorite hobby is playing guitar."
    score_high = clf.predict_importance(text_high)
    print(f"Text: '{text_high}' -> Score: {score_high:.4f}")
    
    text_low = "The weather is nice today."
    score_low = clf.predict_importance(text_low)
    print(f"Text: '{text_low}' -> Score: {score_low:.4f}")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
