import { PostItem } from "@/lib/types";

import { PostCard } from "@/components/post-card";
import { StateBlock } from "@/components/state-block";

interface PostListProps {
  posts: PostItem[];
  isLoading: boolean;
  error: string | null;
  onRetry: () => void;
}


export function PostList({ posts, isLoading, error, onRetry }: PostListProps) {
  if (isLoading) {
    return <StateBlock title="Loading posts" description="Fetching analytics from backend..." />;
  }

  if (error) {
    return (
      <StateBlock
        title="Something went wrong"
        description={error}
        action={
          <button type="button" className="retry-button" onClick={onRetry}>
            Retry
          </button>
        }
      />
    );
  }

  if (!posts.length) {
    return (
      <StateBlock
        title="No posts found"
        description="Try another period or wait until the backend sync stores channel data."
      />
    );
  }

  return (
    <section className="posts-grid">
      {posts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </section>
  );
}
