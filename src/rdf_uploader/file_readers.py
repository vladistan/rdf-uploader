import asyncio
from pathlib import Path


async def count_file_lines(file_path: Path) -> int:
    content = await read_file_content(file_path)
    return len(content.splitlines())


async def read_file_content(file_path: Path) -> str:
    async with asyncio.TaskGroup() as tg:
        task = tg.create_task(
            asyncio.to_thread(lambda: file_path.read_text(encoding="utf-8"))
        )
    return task.result()


def detect_content_type(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    content_types = {
        ".ttl": "text/turtle",
        ".turtle": "text/turtle",
        ".nt": "application/n-triples",
        ".n3": "text/n3",
        ".nq": "application/n-quads",
        ".nquads": "application/n-quads",
        ".rdf": "application/rdf+xml",
        ".xml": "application/rdf+xml",
        ".jsonld": "application/ld+json",
        ".json": "application/rdf+json",
        ".trig": "application/trig",
    }

    return content_types.get(suffix, "text/turtle")


class FileReader:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    async def read_all(self) -> str:
        async with asyncio.TaskGroup() as tg:
            task = tg.create_task(
                asyncio.to_thread(lambda: self.file_path.read_text(encoding="utf-8"))
            )
        return task.result()

    async def count_triples(self) -> int:
        raise NotImplementedError("Subclasses must implement this method")

    async def read_batches(self, batch_size: int = 100) -> list[tuple[str, int]]:
        raise NotImplementedError("Subclasses must implement this method")


class LineBasedReader(FileReader):
    async def count_triples(self) -> int:
        async with asyncio.TaskGroup() as tg:
            task = tg.create_task(asyncio.to_thread(self._count_lines))
        return task.result()

    def _count_lines(self) -> int:
        count = 0
        with self.file_path.open(encoding="utf-8") as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith("#"):
                    count += 1
        return count

    async def read_batches(self, batch_size: int = 100) -> list[tuple[str, int]]:
        def process_file() -> list[tuple[str, int]]:
            result = []
            with self.file_path.open(encoding="utf-8") as f:
                current_lines = []
                current_count = 0
                for line in f:
                    line_stripped = line.strip()
                    if line_stripped and not line_stripped.startswith("#"):
                        current_lines.append(line.rstrip("\n"))
                        current_count += 1
                        if current_count >= batch_size:
                            result.append(("\n".join(current_lines), current_count))
                            current_lines = []
                            current_count = 0

                if current_lines:
                    result.append(("\n".join(current_lines), current_count))
            return result

        return await asyncio.to_thread(process_file)


class WholeFileReader(FileReader):
    async def count_triples(self) -> int:
        content = await self.read_all()
        return content.count(";") + content.count(" .")

    async def read_batches(self, batch_size: int = 100) -> list[tuple[str, int]]:
        content = await self.read_all()
        triple_count = content.count(";") + content.count(" .")
        return [(content, triple_count)]


def get_reader(file_path: Path) -> FileReader:
    suffix = file_path.suffix.lower()

    if suffix in {".nt", ".nq", ".nquads"}:
        return LineBasedReader(file_path)
    return WholeFileReader(file_path)
