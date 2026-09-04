from ml.matching.ats_analyzer import analyze_ats
from ml.recommendation.skill_gap import analyze_skill_gap
from ml.recommendation.role_recommender import recommend_roles
from ml.evaluation.metrics import precision_recall_f1, precision_at_k, mean_reciprocal_rank, ndcg_at_k


def test_ats_analyzer_scores_bounded():
    result = analyze_ats(
        raw_text="Built and deployed a model. Improved accuracy by 15%. " * 20,
        sections_found=["header", "education", "experience", "skills"],
        normalized_skill_count=9,
        experience_raw_texts=["Built and deployed a model, improved accuracy by 15%."],
        achievements=["Won hackathon, ranked top 3%"],
        target_skills=["Python", "Docker"],
        matched_target_skills=2,
    )
    assert 0 <= result.overall_score <= 100
    assert result.disclaimer.startswith("This is an ATS-style analysis")


def test_skill_gap_priorities():
    result = analyze_skill_gap(
        candidate_skills=["Python", "SQL", "Machine Learning", "Git"],
        target_skills=["Python", "Docker", "AWS", "Kubernetes"],
    )
    assert "Python" in result.have
    assert "Docker" in result.missing_high
    assert "AWS" in result.missing_high
    assert result.coverage_pct == 25.0


def test_role_recommender_ranks_ml_engineer_high_for_ml_skills():
    recs = recommend_roles(["Python", "Machine Learning", "PyTorch", "Docker", "SQL"])
    top_roles = [r.role for r in recs[:2]]
    assert "Machine Learning Engineer" in top_roles


def test_evaluation_metrics():
    prf = precision_recall_f1({"a", "b", "c"}, {"a", "b", "d"})
    assert prf["precision"] == round(2 / 3, 4)
    assert prf["recall"] == round(2 / 3, 4)

    p_at_2 = precision_at_k(["x", "y", "z"], {"x", "z"}, k=2)
    assert p_at_2 == 0.5

    mrr = mean_reciprocal_rank([["a", "b", "c"]], [{"b"}])
    assert mrr == 0.5

    ndcg = ndcg_at_k(["a", "b", "c"], {"a": 3, "b": 2, "c": 1}, k=3)
    assert ndcg == 1.0  # already in ideal order


if __name__ == "__main__":
    test_ats_analyzer_scores_bounded()
    test_skill_gap_priorities()
    test_role_recommender_ranks_ml_engineer_high_for_ml_skills()
    test_evaluation_metrics()
    print("ats_and_gap: all tests passed")
