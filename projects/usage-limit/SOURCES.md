# Sources: Usage Limit

Status vocabulary is in `docs/sourcing.md`. Rows 1 and 3 to 7 came from
search-result summaries on 2026-11-02 and are still snippets; no lyric rests
on them. Rows 2 and 8 to 12 were read on 2026-11-03, locally. Row 1's
MacRumors link now redirects to the site's front page. **Upgrade a row by
reading it before any lyric rests on it.**

| # | Claim | Source | Status | Used in |
|---|---|---|---|---|
| 1 | In March 2026, Claude Code users reported usage limits draining far faster than normal, and suspected a bug | [MacRumors, 2026-03-26](https://www.macrumors.com/2026/03/26/claude-code-users-rapid-rate-limit-drain-bug/) | snippet | |
| 2 | Max 20x subscribers reported usage jumping from 21% to 100% on a single prompt during the March 2026 drain | [anthropics/claude-code#38335](https://github.com/anthropics/claude-code/issues/38335) (opened 2026-03-24) says "some reporting jumps from 21% to 100% usage on a single prompt with the Max 20x plan", citing Reddit, not first-hand. A [Pro user's comment](https://github.com/anthropics/claude-code/issues/38335) on 2026-03-30: "From 21%, suddenly hit 100% with routine tasks", not one prompt. The PiunikaWeb article first cited here does **not** contain the figure (it has 52% to 68% to 91% over a session, and 6% on one message) | reported (secondhand: the original Reddit post is not found) | Verse 1 |
| 3 | Anthropic reset Claude Code rate limits after a prompt-caching bug, and confirmed three bugs | search summary of the March coverage; exact source not identified | snippet | |
| 4 | A Pro user reported being locked out after 32 seconds of use | [The Letter Two, 2026-04-01](https://thelettertwo.com/2026/04/01/anthropic-claude-rate-limit-backlash/) (probably; the summary did not say which article) | snippet | |
| 5 | r/ClaudeAI ran a moderator "usage limits discussion megathread" from late March 2026, and logged a surge of session-limit reports in early May | [megathread (mirror)](https://redlib.groet-infra.nl/r/ClaudeAI/comments/1s7fcjf/claude_usage_limits_discussion_megathread_ongoing/), [May log (mirror)](https://redlib.groet-infra.nl/r/ClaudeAI/comments/1t33k25/rclaudeai_user_problem_report_log_and_surge/) | snippet | |
| 6 | Negative Google Play reviews of the Claude app rose 3.4x in September 2026, citing strict usage limits among other issues | [Unstar.app](https://unstar.app/events/claude-by-anthropic-android-complaints-september-2026), a third-party aggregator | snippet (weak source) | |
| 7 | During a June 2026 outage, a popular meme said "Claude is down, and management just discovered I'm supposed to know how to code without it" | [LatestLY](https://www.latestly.com/social-viral/claude-down-funny-memes-flood-social-media-as-users-report-outages-developers-joke-about-returning-to-manual-coding-7478848.html) | snippet | |
| 8 | Paid plans have a session limit that resets every five hours, starting from the first message | [Claude Help Center, "How do usage and length limits work?"](https://support.claude.com/en/articles/11647753-understanding-usage-and-length-limits), read 2026-11-03: the period "starts when you send your first message, and your limit resets in full five hours later" | verified | Hook ("come back at five") |
| 9 | Paid plans also have a weekly limit, separate from the five-hour one, so waiting five hours does not clear it. Announced 2025-07-28, in effect from 2025-08-28 for Pro and both Max tiers | Help Center page in row 8 ("weekly limits that reset once every week"), read 2026-11-03; [TechCrunch, 2025-07-28](https://techcrunch.com/2025/07/28/anthropic-unveils-new-rate-limits-to-curb-claude-code-power-users/): the weekly limits "will go into effect August 28", and the five-hour limits "will remain in place". The earlier claim that the reset day varies by account is unverified and dropped | verified | Hook (final) |
| 10 | Claude Code's limit messages are "You've hit your session limit" and "You've hit your weekly limit", and the message shows when the window resets | [Claude Code docs, Manage costs](https://code.claude.com/docs/en/costs#when-a-developer-asks-about-a-limit), read 2026-11-03 | verified | Hook (paraphrased as "limit reached, come back at five", so it does not quote it) |
| 11 | "You're absolutely right!" is a widely mocked Claude Code habit | [The Register, 2025-08-13](https://www.theregister.com/2025/08/13/claude_codes_copious_coddling_confounds/), Thomas Claburn: GitHub issue #3382 complained Claude says it "about everything"; 48 open issues cited the phrase; social threads mocked it | reported | Verse 1, Bridge |
| 12 | Claude Code shows "Compacting conversation…" when it summarises the history to free context | [Claude Code docs, prompt caching](https://code.claude.com/docs/en/prompt-caching#compacting-the-conversation) ("Compaction replaces your message history with a summary"), read 2026-11-03; the exact string `Compacting conversation…` is in the Claude Code 2.1.309 binary on this machine | verified | Verse 1 |

## Side material (other trending topics, usable as bars)

| # | Claim | Source | Status |
|---|---|---|---|
| S1 | Anthropic reported $16.95B in Q3 revenue and a $23.29B net loss, ahead of an IPO expected in November 2026 | [The National, 2026-11-02](https://www.thenationalnews.com/news/us/2026/11/02/anthropic-reports-17bn-in-q3-revenue-before-supersized-ipo/) | snippet |
| S2 | Anthropic's usage policy bans "sustained and needless abusive or cruel behavior toward our models", which set off Terminator memes | [Yahoo Tech / Fast Company](https://tech.yahoo.com/ai/claude/articles/anthropic-wants-stop-bullying-claude-200500028.html) | snippet |
