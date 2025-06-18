# Instagram influencer + Post monitor with TikHub API
[Notion](https://www.notion.so/Instagram-Influencer-Post-Monitor-with-TikHub-API-3days-2120b6d0767780ceb666d14cd26ee323?source=copy_link)

Your task is to build a lightweight monitoring service using TikHub's API, with Redis, Celery, FastAPI, and MySQL. You'll deploy two features: Instagram Influencer Monitor and Post Monitor. All data is stored locally in MySQL and Redis, and exposed via FastAPI endpoints.


## 1. Influencer Monitor
```
Purpose: Track basic metrics for one or more instagram users over time.
```

### User Inputs
- Instagram username
- Monitoring interval:
    - 30 seconds
    - 30 minutes
    - 1 hour
    - 1 day
    - 7 days

### Metrics to Record
- Instagram Username
- user id ( some identification )
- Follower count
- Following count
- Post count
- (Optional) Engagement rate, bio info, etc. (Feel free to discuss with me which data needs to be storaged)

### API Endpoints

| Endpoint | Description |
|-|-|
| POST `/api/v1/tiktok/influencer_monitor/create_monitor_task` | Create a new monitoring task |
| GET `/api/v1/tiktok/influencer_monitor/user_history/{user_identifier}` | Retrieve historical data for a monitored user |
| GET `/api/v1/tiktok/influencer_monitor/tasks` | List all influencer monitoring tasks |
| POST `/api/v1/tiktok/influencer_monitor/stop_tasks` | Stop one or more monitoring tasks |
| GET `/api/v1/tiktok/influencer_monitor/task_status/{task_id}` | Get status for a specific monitoring task |
| POST `/api/v1/tiktok/influencer_monitor/pause_task/{task_id}` | Pause a monitoring task |
| POST `/api/v1/tiktok/influencer_monitor/resume_task/{task_id}` | Resume a paused monitoring task |


## 2. Post Monitor
```
Purpose: Track engagement data for specific instagram posts.
```

### User Inputs
- Post URL or Post ID

### Metrics to Record
- like_count
- comment_count
- if a video: play_count

### API Endpoints

|Endpoint| Description |
| --- | --- |
| POST `/api/v1/tiktok/monitor/create_monitor_task` | Start tracking a given post |
| GET `/api/v1/tiktok/monitor/video_history/{aweme_id}` | Retrieve historical engagement data for the post |
| GET `/api/v1/tiktok/monitor/tasks` | List all post monitoring tasks |
| POST `/api/v1/tiktok/monitor/stop_tasks` | Stop one or more post monitoring tasks |
| GET `/api/v1/tiktok/monitor/task_status/{task_id}` | Check the status of a post monitoring task |
| POST `/api/v1/tiktok/monitor/pause_task/{task_id}` | Pause tracking for a post |
| POST `/api/v1/tiktok/monitor/resume_task/{task_id}` | Resume tracking for a paused post task |

## Technical Stack
- **API server**: FastAPI
- **Task queue/scheduler**: Celery (with Redis as broker + backend)
- **Data storage**: MySQL (local instance)
- **Cache/state management**: Redis

## Deliverables
1. **Fully functional FastAPI application with all endpoints implemented.**
2. Celery workers that fetch data from TikHub's API at the specified intervals.
3. Redis + MySQL local setup with appropriate schema and task state tracking.
4. Clear README with setup, run instructions, and examples.
