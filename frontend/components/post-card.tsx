import { formatDate, formatNumber, truncateText } from "@/lib/format";
import { PostItem } from "@/lib/types";

interface PostCardProps {
  post: PostItem;
}


//карточка поста
export function PostCard({ post }: PostCardProps) {
  return (
    <article className="post-card">
      <div className="post-head">
        <div>
          <p className="post-channel">{post.channel_title || `@${post.channel_username}`}</p>
          <p className="post-date">{formatDate(post.message_date)}</p>
          {post.is_alert_candidate ? <p className="post-alert">alert candidate in first 8h</p> : null}
        </div>
        <a className="post-link" href={post.telegram_url} target="_blank" rel="noreferrer">
          Open
        </a>
      </div>

      <p className="post-text">{truncateText(post.text)}</p>
      {post.alert_threshold_views > 0 ? (
        <p className="post-threshold">
          Threshold 50%: {formatNumber(post.alert_threshold_views)} from median{" "}
          {formatNumber(post.channel_median_views)}
        </p>
      ) : null}

      <dl className="metrics-grid">
        <div>
          <dt>Views</dt>
          <dd>{formatNumber(post.views)}</dd>
        </div>
        <div>
          <dt>Forwards</dt>
          <dd>{formatNumber(post.forwards)}</dd>
        </div>
        <div>
          <dt>Reactions</dt>
          <dd>{formatNumber(post.reactions_total)}</dd>
        </div>
        <div>
          <dt>Replies</dt>
          <dd>{formatNumber(post.replies_count)}</dd>
        </div>
        <div className="score-block">
          <dt>Alert score</dt>
          <dd>{formatNumber(post.popularity_score)}</dd>
        </div>
      </dl>
    </article>
  );
}
