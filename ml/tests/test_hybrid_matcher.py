from ml.matching.hybrid_matcher import compute_hybrid_match, explain_match, DEFAULT_WEIGHTS


def _base_kwargs(**overrides):
    kwargs = dict(
        semantic_similarity=0.9,
        candidate_skills=["Python", "Machine Learning", "PyTorch", "SQL"],
        required_skills=["Python", "PyTorch", "AWS"],
        candidate_years_experience=2,
        required_years_experience=1,
        candidate_education_level="bachelor",
        required_education_level="bachelor",
        candidate_titles=["Machine Learning Intern"],
        target_role="Machine Learning Engineer",
        resume_quality_score=82,
    )
    kwargs.update(overrides)
    return kwargs


def test_overall_score_in_range():
    result = compute_hybrid_match(**_base_kwargs())
    assert 0 <= result.overall_score <= 100


def test_perfect_match_scores_high():
    result = compute_hybrid_match(**_base_kwargs(
        semantic_similarity=1.0,
        candidate_skills=["Python", "PyTorch", "AWS", "Machine Learning"],
        required_skills=["Python", "PyTorch", "AWS"],
        candidate_years_experience=5, required_years_experience=1,
        resume_quality_score=100,
    ))
    assert result.overall_score >= 90
    assert result.missing_skills == []


def test_missing_skills_detected():
    result = compute_hybrid_match(**_base_kwargs())
    assert "AWS" in result.missing_skills
    assert "Python" in result.matched_skills


def test_weights_must_sum_to_one():
    bad_weights = dict(DEFAULT_WEIGHTS)
    bad_weights["semantic_similarity"] = 0.99  # now sums > 1
    try:
        compute_hybrid_match(**_base_kwargs(weights=bad_weights))
        assert False, "should have raised"
    except ValueError:
        pass


def test_explain_match_produces_readable_output():
    result = compute_hybrid_match(**_base_kwargs())
    explanation = explain_match(result)
    assert "strengths" in explanation and "gaps" in explanation
    assert isinstance(explanation["strengths"], list)


def test_low_experience_reduces_score_proportionally():
    full = compute_hybrid_match(**_base_kwargs(candidate_years_experience=4, required_years_experience=4))
    half = compute_hybrid_match(**_base_kwargs(candidate_years_experience=2, required_years_experience=4))
    assert full.experience > half.experience


if __name__ == "__main__":
    test_overall_score_in_range()
    test_perfect_match_scores_high()
    test_missing_skills_detected()
    test_weights_must_sum_to_one()
    test_explain_match_produces_readable_output()
    test_low_experience_reduces_score_proportionally()
    print("hybrid_matcher: all tests passed")
