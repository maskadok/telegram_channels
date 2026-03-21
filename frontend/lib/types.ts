export type PeriodFilter = "7d" | "30d" | "90d" | "all";

export interface ChannelItem {
  id: number;
  username: string;
  title: string;
  is_active: boolean;
  posts_count: number;
  latest_post_date: string | null;
  updated_at: string;
}

export interface PostItem {
  id: number;
  channel_id: number;
  channel_username: string;
  channel_title: string;
  telegram_message_id: number;
  message_date: string;
  text: string | null;
  views: number;
  forwards: number;
  replies_count: number;
  reactions_total: number;
  channel_median_views: number;
  alert_threshold_views: number;
  popularity_score: number;
  is_alert_candidate: boolean;
  alerted_at: string | null;
  collected_at: string;
  telegram_url: string;
}
