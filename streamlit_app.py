import os
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime
import pytz
import isodate

# Load environment variables (local dev) and prefer Streamlit secrets (deploy)
load_dotenv()

# Configuration: prefer st.secrets when available, fallback to env vars
YOUTUBE_API_KEY = (
    (st.secrets.get("YOUTUBE_API_KEY") if hasattr(st, "secrets") else None)
    or os.getenv('YOUTUBE_API_KEY')
)
REGION_CODE = (
    (st.secrets.get("REGION_CODE") if hasattr(st, "secrets") else None)
    or os.getenv('REGION_CODE')
    or 'KR'
)
MAX_RESULTS = 30

def setup_youtube_client():
    """Initialize and return the YouTube API client."""
    try:
        return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    except Exception as e:
        st.error(f"Error initializing YouTube API client: {e}")
        return None

def get_popular_videos(youtube):
    """Fetch popular videos from YouTube."""
    try:
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            regionCode=REGION_CODE,
            maxResults=MAX_RESULTS
        )
        response = request.execute()
        return response.get('items', [])
    except HttpError as e:
        st.error(f"YouTube API error: {e}")
        return []
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

def get_channel_stats(youtube, channel_ids):
    """Return a mapping of channelId -> subscriberCount (string)."""
    stats = {}
    try:
        if not channel_ids:
            return stats
        # API allows up to 50 ids per request
        ids = list(channel_ids)
        chunks = [ids[i:i+50] for i in range(0, len(ids), 50)]
        for chunk in chunks:
            req = youtube.channels().list(
                part="statistics",
                id=",".join(chunk),
                maxResults=50,
            )
            res = req.execute()
            for item in res.get('items', []):
                cid = item.get('id')
                stt = item.get('statistics', {})
                # Some channels hide subscribers; subscriberCount may be missing
                sub = stt.get('subscriberCount')
                stats[cid] = sub
    except HttpError as e:
        st.warning(f"채널 통계 조회 오류: {e}")
    except Exception as e:
        st.warning(f"채널 통계 처리 중 오류: {e}")
    return stats

def format_view_count(views):
    """Format view count to be more readable."""
    try:
        views = int(views)
        if views >= 100000000:
            return f"{views/100000000:.1f}억회"
        elif views >= 10000:
            return f"{views/10000:.1f}만회"
        return f"{views:,}회"
    except (ValueError, TypeError):
        return views

def format_duration(duration_iso):
    """Format ISO 8601 duration to a readable format."""
    try:
        duration = isodate.parse_duration(duration_iso)
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        seconds = duration.seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    except Exception:
        return duration_iso

def format_count(count):
    """Format counts (likes, comments) to be more readable."""
    try:
        count = int(count)
        if count >= 10000:
            return f"{count/10000:.1f}만"
        return f"{count:,}"
    except (ValueError, TypeError):
        return count

def display_videos(videos, channel_stats=None):
    """Display videos in a grid layout."""
    if not videos:
        st.warning("No videos found.")
        return
    
    for i, video in enumerate(videos, 1):
        snippet = video.get('snippet', {})
        stats = video.get('statistics', {})
        content_details = video.get('contentDetails', {})
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Display thumbnail with duration overlay
            thumbnail_url = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
            duration = format_duration(content_details.get('duration', ''))
            
            if thumbnail_url:
                try:
                    # Newer Streamlit versions
                    st.image(thumbnail_url, use_container_width=True)
                except TypeError:
                    # Backward compatibility with older versions
                    st.image(thumbnail_url, use_column_width=True)
                st.caption(duration)
        
        with col2:
            # Video title with link
            title = snippet.get('title', 'No title')
            video_id = video.get('id')
            if video_id:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                st.markdown(f"### [{title}]({video_url})")
            else:
                st.markdown(f"### {title}")
            
            # Channel name + subscribers
            channel_title = snippet.get('channelTitle', 'Unknown channel')
            channel_id = snippet.get('channelId')
            subs_raw = (channel_stats or {}).get(channel_id)
            subs_txt = (
                f"구독자 {format_count(subs_raw)}"
                if subs_raw is not None else "구독자 비공개"
            )
            st.write(f"**채널:** {channel_title} • {subs_txt}")
            
            # View count and publish date
            view_count = format_view_count(stats.get('viewCount', 'N/A'))
            like_count = format_count(stats.get('likeCount', 'N/A'))
            comment_count = format_count(stats.get('commentCount', 'N/A'))
            
            published_at = snippet.get('publishedAt', '')
            try:
                publish_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
                kst = pytz.timezone('Asia/Seoul')
                publish_date = pytz.utc.localize(publish_date).astimezone(kst)
                publish_date_str = publish_date.strftime('%Y.%m.%d')
                
                # Display metrics in a compact row
                metrics = [
                    f"👁️ {view_count}",
                    f"👍 {like_count}",
                    f"💬 {comment_count}",
                    f"📅 {publish_date_str}"
                ]
                st.write(" • ".join(metrics))
            except (ValueError, TypeError):
                st.write(f"👁️ {view_count} • 👍 {like_count} • 💬 {comment_count}")
        
        # Add a divider between videos
        if i < len(videos):
            st.divider()

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="인기 동영상",
        page_icon="▶️",
        layout="wide"
    )
    
    st.title("🔥 인기 동영상")
    st.caption(f"현재 {REGION_CODE} 지역의 인기 동영상을 보여줍니다.")
    
    if not YOUTUBE_API_KEY:
        st.error("⚠️ YouTube API 키가 설정되지 않았습니다. .streamlit/secrets.toml 또는 .env 파일을 확인해주세요.")
        st.code("""
[secrets.toml]
YOUTUBE_API_KEY = "your_youtube_api_key_here"
REGION_CODE = "KR"
""".strip(), language="toml")
        return
    
    # Refresh button
    if st.button("🔄 새로고침", type="primary"):
        st.rerun()
    
    # Initialize YouTube client
    youtube = setup_youtube_client()
    if not youtube:
        return
    
    # Show loading state
    with st.spinner('인기 동영상을 불러오는 중...'):
        # Fetch and display videos
        videos = get_popular_videos(youtube)
        # Fetch channel subscriber counts
        channel_ids = {v.get('snippet', {}).get('channelId') for v in videos if v.get('snippet', {}).get('channelId')}
        channel_stats = get_channel_stats(youtube, channel_ids)
        display_videos(videos, channel_stats)

if __name__ == "__main__":
    main()
