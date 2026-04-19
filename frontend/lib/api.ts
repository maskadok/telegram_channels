import { ChannelItem, PeriodFilter, PostItem } from "./types";

//клиент для api
async function apiRequest<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}


//базовый адрес api
function getApiBaseUrl(): string {
  const envBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "");
  if (envBaseUrl) {
    return envBaseUrl;
  }

  if (typeof window !== "undefined") {
    return window.location.origin;
  }

  return "http://localhost:8000";
}


export async function fetchChannels(): Promise<ChannelItem[]> {
  return apiRequest<ChannelItem[]>("/api/channels");
}


export async function fetchTopPosts(params: {
  period: PeriodFilter;
  channelUsername?: string;
  limit?: number;
}): Promise<PostItem[]> {
  //загрузка свежих постов
  const query = new URLSearchParams();
  query.set("period", params.period);
  query.set("limit", String(params.limit ?? 20));

  if (params.channelUsername) {
    query.set("channel_username", params.channelUsername);
  }

  return apiRequest<PostItem[]>(`/api/posts/top?${query.toString()}`);
}
