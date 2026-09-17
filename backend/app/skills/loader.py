from pathlib import Path


SKILLS_DIR = Path(__file__).resolve().parent


def list_skills() -> list[str]:
    skills = []

    for path in SKILLS_DIR.iterdir():
        if path.is_dir() and (path / "SKILL.md").exists():
            skills.append(path.name)

    return sorted(skills)


def load_skill(skill_name: str) -> str:
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"

    if not skill_path.exists():
        raise ValueError(
            f"Skill '{skill_name}' was not found."
        )

    return skill_path.read_text(
        encoding="utf-8"
    )