import sys


def monitor(app):
    from celery.events import EventReceiver

    state = app.events.State()

    def announce_failed_tasks(event):
        state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = state.tasks.get(event["uuid"])

        sys.stdout.write(
            "TASK FAILED: %s[%s] %s\n"
            % (
                task.name,
                task.uuid,
                task.info(),
            )
        )

    def on_event(event):
        if event["type"] != "worker-heartbeat":
            state.event(event)

    with app.connection() as connection:
        recv = EventReceiver(connection, handlers={"*": on_event})
        recv.capture(limit=None, timeout=None)


def run():
    import django

    django.setup()
    from country_workspace.config.celery import app

    monitor(app)


if __name__ == "__main__":
    run()
