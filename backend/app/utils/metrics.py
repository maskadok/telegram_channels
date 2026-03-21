from statistics import median


ANALYTICS_LOOKBACK_DAYS = 90
ALERT_WINDOW_HOURS = 8
ALERT_SHARE_FROM_MEDIAN = 0.5


#медиана просмотров
def calculate_channel_median_views(values: list[int]) -> float:
    normalized = [int(value or 0) for value in values if int(value or 0) > 0]
    if not normalized:
        return 0.0
    return round(float(median(normalized)), 2)


#порог алерта
def calculate_alert_threshold(channel_median_views: float) -> float:
    if channel_median_views <= 0:
        return 0.0
    return round(channel_median_views * ALERT_SHARE_FROM_MEDIAN, 2)


#скор против порога
def calculate_popularity_score(
    views: int,
    alert_threshold_views: float,
) -> float:
    if alert_threshold_views <= 0:
        return 0.0
    return round(((views or 0) / alert_threshold_views) * 100, 2)


#проверка окна
def should_alert_post(
    age_hours: float,
    views: int,
    alert_threshold_views: float,
) -> bool:
    if age_hours < 0 or age_hours > ALERT_WINDOW_HOURS:
        return False
    if alert_threshold_views <= 0:
        return False
    return (views or 0) >= alert_threshold_views
