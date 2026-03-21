"use client";

import { useEffect, useState } from "react";

import { FilterBar } from "@/components/filter-bar";
import { PostList } from "@/components/post-list";
import { StateBlock } from "@/components/state-block";
import { fetchChannels, fetchTopPosts } from "@/lib/api";
import { ChannelItem, PeriodFilter, PostItem } from "@/lib/types";


export function DashboardPage() {
  const [channels, setChannels] = useState<ChannelItem[]>([]);
  const [posts, setPosts] = useState<PostItem[]>([]);
  const [selectedChannel, setSelectedChannel] = useState("");
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodFilter>("7d");
  const [channelsLoading, setChannelsLoading] = useState(true);
  const [postsLoading, setPostsLoading] = useState(true);
  const [channelsError, setChannelsError] = useState<string | null>(null);
  const [postsError, setPostsError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadChannels() {
      setChannelsLoading(true);
      setChannelsError(null);

      try {
        const result = await fetchChannels();
        if (!cancelled) {
          setChannels(result);
        }
      } catch (error) {
        if (!cancelled) {
          setChannelsError(error instanceof Error ? error.message : "failed to load channels");
        }
      } finally {
        if (!cancelled) {
          setChannelsLoading(false);
        }
      }
    }

    loadChannels();

    return () => {
      cancelled = true;
    };
  }, [reloadToken]);

  useEffect(() => {
    let cancelled = false;

    async function loadPosts() {
      setPostsLoading(true);
      setPostsError(null);

      try {
        const result = await fetchTopPosts({
          period: selectedPeriod,
          channelUsername: selectedChannel || undefined,
          limit: 20,
        });
        if (!cancelled) {
          setPosts(result);
        }
      } catch (error) {
        if (!cancelled) {
          setPostsError(error instanceof Error ? error.message : "failed to load posts");
          setPosts([]);
        }
      } finally {
        if (!cancelled) {
          setPostsLoading(false);
        }
      }
    }

    loadPosts();

    return () => {
      cancelled = true;
    };
  }, [selectedChannel, selectedPeriod, reloadToken]);

  function handleRetry() {
    setReloadToken((value) => value + 1);
  }

  return (
    <div className="dashboard-stack">
      <section className="hero-card">
        <p className="eyebrow">telegram analytics</p>
        <h1>Early signal posts</h1>
        <p className="hero-text">
          A lightweight dashboard that highlights posts with strong early views against the
          channel baseline. Works inside Telegram Mini App and in a normal browser.
        </p>
      </section>

      {channelsError ? (
        <StateBlock
          title="Channels are unavailable"
          description={channelsError}
          action={
            <button type="button" className="retry-button" onClick={handleRetry}>
              Retry
            </button>
          }
        />
      ) : (
        <FilterBar
          channels={channels}
          selectedChannel={selectedChannel}
          selectedPeriod={selectedPeriod}
          onChannelChange={setSelectedChannel}
          onPeriodChange={setSelectedPeriod}
          disabled={channelsLoading}
        />
      )}

      <div className="section-head">
        <div>
          <p className="section-label">results</p>
          <h2>Signal feed</h2>
        </div>
        <p className="section-meta">
          {selectedChannel ? `@${selectedChannel}` : "All channels"} | {selectedPeriod}
        </p>
      </div>

      <PostList posts={posts} isLoading={postsLoading} error={postsError} onRetry={handleRetry} />
    </div>
  );
}
