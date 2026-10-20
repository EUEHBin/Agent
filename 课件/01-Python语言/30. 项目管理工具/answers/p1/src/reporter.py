import os
import aiofiles
from datetime import datetime
from src.config import OUTPUT_DIR


async def save_report(topic: str, content: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic: str = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)[:20]
    filename: str = f"{safe_topic}_调研报告_{timestamp}.md"
    filepath: str = os.path.join(OUTPUT_DIR, filename)

    async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
        await f.write(content)

    return os.path.abspath(filepath)
