async def get_or_create_topic(app, channel_id, topic_name):

    peer = await app.resolve_peer(channel_id)

    # Fetch existing topics
    result = await app.invoke(
        GetForumTopics(
            channel=peer,
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=100
        )
    )

    # Find an existing one
    for t in result.topics:
        if t.title.lower() == topic_name.lower():
            return t.id

    # Create new topic
    print(f"🧵 Creating Topic: {topic_name}")

    res = await app.invoke(
        CreateForumTopic(
            channel=peer,
            title=topic_name,
            icon_color=0x6FB9F0
        )
    )

    return res.topic.id
