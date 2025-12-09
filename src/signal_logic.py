def decide_direction(count_h, count_v, ambulance_detected=False):
    if ambulance_detected:
        return "Emergency"
    
    # Adaptive Logic: Green for the side with MORE traffic
    return "Horizontal" if count_h >= count_v else "Vertical"


def congestion_level(total):
    if total > 25:
        return "High"
    elif total > 10:
        return "Medium"
    else:
        return "Low"
