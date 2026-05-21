from typing import Dict, List, Optional

class CitationDatabase:
    """
    In-memory reference dictionary binder. Map paper source IDs to rich metadata
    to build reference records and export details.
    """
    def __init__(self):
        self._db: Dict[str, dict] = {}

    def add_paper(self, paper: dict):
        if not paper or "id" not in paper:
            return
        pid = paper["id"]
        if pid not in self._db:
            self._db[pid] = paper

    def add_papers(self, papers: List[dict]):
        for paper in papers:
            self.add_paper(paper)

    def get_paper(self, source_id: str) -> Optional[dict]:
        return self._db.get(source_id)

    def get_all(self) -> List[dict]:
        return list(self._db.values())

    def format_apa(self, source_id: str) -> str:
        paper = self.get_paper(source_id)
        if not paper:
            return f"[{source_id}] Reference not found."
            
        authors = paper.get("authors", "Unknown Authors")
        year = paper.get("year", "n.d.")
        title = paper.get("title", "Untitled Document")
        source = paper.get("source", "Web Resource")
        url = paper.get("url", "")
        
        ref = f"{authors} ({year}). {title}. *{source}*."
        if url:
            ref += f" Available at: {url}"
        return ref
