import os

from apscheduler.schedulers.blocking import BlockingScheduler

from backend.app.automation.daily_tasks import run_daily_task_summary
from backend.app.automation.task_monitor import check_unfinished_tasks


TIMEZONE = os.getenv(
    "AUTOMATION_TIMEZONE",
    "Asia/Riyadh",
)

DAILY_SUMMARY_HOUR = int(
    os.getenv(
        "DAILY_SUMMARY_HOUR",
        "9",
    )
)

TASK_MONITOR_MINUTES = int(
    os.getenv(
        "TASK_MONITOR_MINUTES",
        "60",
    )
)


def start_scheduler():
    scheduler = BlockingScheduler(
        timezone=TIMEZONE
    )

    scheduler.add_job(
        run_daily_task_summary,
        trigger="cron",
        hour=DAILY_SUMMARY_HOUR,
        minute=0,
        id="daily_task_summary",
        replace_existing=True,
    )

    scheduler.add_job(
        check_unfinished_tasks,
        trigger="interval",
        minutes=TASK_MONITOR_MINUTES,
        id="unfinished_task_monitor",
        replace_existing=True,
    )

    print("Automation scheduler started.")

    print(
        f"Daily task summary: every day at "
        f"{DAILY_SUMMARY_HOUR:02d}:00."
    )

    print(
        f"Task monitor: every "
        f"{TASK_MONITOR_MINUTES} minute(s)."
    )

    print(
        f"Timezone: {TIMEZONE}"
    )

    print("Press Ctrl+C to stop.")

    try:
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        print(
            "\nAutomation scheduler stopped."
        )


if __name__ == "__main__":
    start_scheduler()