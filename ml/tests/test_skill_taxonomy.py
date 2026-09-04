from ml.extraction.skill_taxonomy import normalize_skill, normalize_skills


def test_reactjs_variants_normalize_to_react():
    for variant in ["React.js", "React JS", "ReactJS", "react-js", "react"]:
        result = normalize_skill(variant)
        assert result.canonical == "React", f"{variant} -> {result.canonical}"
        assert result.matched


def test_ml_variants_normalize_to_machine_learning():
    for variant in ["ML", "Machine Learning", "machine-learning", "machine_learning"]:
        result = normalize_skill(variant)
        assert result.canonical == "Machine Learning"


def test_unknown_skill_passthrough():
    result = normalize_skill("Some Totally New Tool")
    assert result.matched is False
    assert result.canonical == "Some Totally New Tool"


def test_normalize_skills_deduplicates():
    raw = ["React", "React.js", "ReactJS", "Python", "python3"]
    normalized = normalize_skills(raw)
    canonicals = {r.canonical for r in normalized}
    assert canonicals == {"React", "Python"}
    assert len(normalized) == 2


if __name__ == "__main__":
    test_reactjs_variants_normalize_to_react()
    test_ml_variants_normalize_to_machine_learning()
    test_unknown_skill_passthrough()
    test_normalize_skills_deduplicates()
    print("skill_taxonomy: all tests passed")
