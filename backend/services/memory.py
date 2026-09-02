from collections import defaultdict
from datetime import datetime, timezone


class ConversationMemory:

    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages

        self.conversations = defaultdict(list)
        self.meta = {}

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ):
        self.conversations[conversation_id].append(
            {
                "role": role,
                "content": content,
            }
        )

        self.meta[conversation_id] = {
            "conversation_id": conversation_id,
            "title": self.meta.get(
                conversation_id,
                {}
            ).get(
                "title",
                "Chat"
            ),
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        if role == "user" and content.strip():
            title = content.strip()
            if len(title) > 36:
                title = title[:33] + "..."
            self.meta[conversation_id]["title"] = title

        # Keep only the latest messages
        self.conversations[conversation_id] = (
            self.conversations[conversation_id]
            [-self.max_messages:]
        )

    def get_history(
        self,
        conversation_id: str,
    ):
        return self.conversations.get(
            conversation_id,
            [],
        )

    def list_conversations(self):
        conversations = []

        for conversation_id, messages in self.conversations.items():
            meta = self.meta.get(
                conversation_id,
                {"title": "Chat"},
            )
            conversations.append(
                {
                    "conversation_id": conversation_id,
                    "title": meta.get(
                        "title",
                        "Chat",
                    ),
                    "message_count": len(messages),
                    "updated_at": meta.get(
                        "updated_at",
                        None,
                    ),
                }
            )

        conversations.sort(
            key=lambda item: (
                item.get("updated_at") or "",
                item.get("conversation_id", ""),
            ),
            reverse=True,
        )

        return conversations

    def clear(
        self,
        conversation_id: str,
    ):
        self.conversations.pop(
            conversation_id,
            None,
        )
        self.meta.pop(
            conversation_id,
            None,
        )


memory = ConversationMemory()
