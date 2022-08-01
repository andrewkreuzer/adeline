async def create_event_blocks(context, next):
    event_blocks = []
    for event in context["events"]:
        event_blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"# {event['name']}\n{event['kind']}",
                },
            }
        )
        event_blocks.append({"type": "divider"})

    context["event_blocks"] = event_blocks
    await next()


async def update_home_tab(context, client, event, logger):
    try:
        await client.views_publish(
            user_id=event["user"],
            view={
                "type": "home",
                "blocks": context["event_blocks"],
            },
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
