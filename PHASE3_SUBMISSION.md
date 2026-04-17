# CineMetrics - Phase 3 Submission

## Project Links

| Description | Link |
| :---- | :---- |
| Link to shared copy of this exact Google Doc | [TO BE FILLED BY TEAM] |
| Github Project Repo Link | https://github.com/ghkim887/CineMetrics |
| Link to shared demo video | [TO BE FILLED BY TEAM - must be publicly visible] |

## REST API Matrix

| Resource | GET | POST | PUT | DELETE |
| :---- | :---- | :---- | :---- | :---- |
| /movies | List movies w/ filters (genre, year, country, language, search) [Jake-1], [Jake-6], [Priya-4] | Add new movie [Marcus-1] | n/a | n/a |
| /movies/{id} | Movie detail + genres [Priya-3] | n/a | Update metadata [Marcus-2] | Soft-delete (status='removed') [Marcus-3] |
| /movies/{id}/similar | Movies sharing genres [Priya-3] | n/a | n/a | n/a |
| /movies/{id}/reviews | Reviews for movie [Priya-5] | n/a | n/a | n/a |
| /users/{id}/recommendations | Personalized recs [Jake-2] | n/a | n/a | n/a |
| /users/{id}/history | Watch history [Priya-2] | Mark watched [Jake-3] | n/a | n/a |
| /users/{id}/ratings | User's ratings [Jake-5] | Submit rating [Jake-5] | n/a | n/a |
| /users/{id}/stats | Viewing stats (total, genres, avg) [Priya-2] | n/a | n/a | n/a |
| /watchlists/user/{id} | User's watchlists [Jake-4] | n/a | n/a | n/a |
| /watchlists | n/a | Create watchlist [Jake-4] | n/a | n/a |
| /watchlists/{id}/items | Watchlist items [Jake-4] | Add to watchlist [Jake-4] | n/a | n/a |
| /watchlists/{id}/items/{item_id} | n/a | n/a | n/a | Remove from watchlist [Jake-4] |
| /reviews | List reviews (filterable) [Marcus-4], [Priya-5] | Create review [Priya-1] | n/a | n/a |
| /reviews/{id} | Single review detail | n/a | Update review [Priya-6], [Marcus-4] | Soft-delete review [Priya-6] |
| /reviews/{id}/flags | n/a | Flag review [Marcus-4] | n/a | n/a |
| /recommendations/user/{id} | All recs for user [Jake-2] | n/a | n/a | n/a |
| /recommendations/{id} | Single recommendation [Jake-2] | n/a | n/a | n/a |
| /recommendations/{id}/click | n/a | Record click [Elena-3] | n/a | n/a |
| /recommendations/generate/{id} | Generate new recs [Jake-2] | n/a | n/a | n/a |
| /recommendations/{id}/clicks | Clicks for a rec [Elena-3] | n/a | n/a | n/a |
| /admin/users | List all users [Marcus-5] | n/a | n/a | n/a |
| /admin/users/{id} | n/a | n/a | Update user status (ban/deactivate) [Marcus-5] | n/a |
| /admin/logs | Recent admin logs [Marcus-6] | n/a | n/a | n/a |
| /admin/reviews/flagged | Flagged reviews [Marcus-4] | n/a | n/a | n/a |
| /admin/reviews/{id}/moderate | n/a | n/a | Moderate review [Marcus-4] | n/a |
| /analytics/ratings-distribution | Rating histogram [Elena-1] | n/a | n/a | n/a |
| /analytics/trending-genres | Genre trends by period [Elena-2] | n/a | n/a | n/a |
| /analytics/click-through-rates | CTR by user segment [Elena-3] | n/a | n/a | n/a |
| /analytics/top-movies | Top-reviewed/rated movies [Elena-4] | n/a | n/a | n/a |
| /analytics/engagement | Engagement metrics [Elena-5] | n/a | n/a | n/a |
| /analytics/export | CSV download [Elena-6] | n/a | n/a | n/a |

## Summary

The CineMetrics REST API is organized into 7 logical blueprints (movies, users, reviews, watchlists, recommendations, admin, analytics) with 30+ routes spanning all four HTTP verbs (GET, POST, PUT, DELETE). Every user story across all four personas is fully addressed by one or more API routes, with corresponding Streamlit feature pages providing the user interface.

## Route Statistics

| Blueprint | GET | POST | PUT | DELETE | Total |
| :---- | :---- | :---- | :---- | :---- | :---- |
| movies | 4 | 1 | 1 | 1 | 7 |
| users | 4 | 2 | 0 | 0 | 6 |
| reviews | 2 | 2 | 1 | 1 | 6 |
| watchlists | 2 | 2 | 0 | 1 | 5 |
| recommendations | 4 | 1 | 0 | 0 | 5 |
| admin | 3 | 0 | 2 | 0 | 5 |
| analytics | 6 | 0 | 0 | 0 | 6 |
| **TOTAL** | **25** | **8** | **4** | **3** | **40** |
