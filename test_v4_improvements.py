"""
v4 개선사항 테스트 - 샘플 텍스트로 점수 변화 확인
"""
import sys
sys.path.insert(0, r'c:\exam\pdf_project')

from auto_grade_all import score_problem_definition, score_reflection

print("="*80)
print("v4 개선사항 테스트")
print("="*80)

# 테스트 1: 짧지만 내용 있는 문제 정의
test1 = """
고령층의 건강기능식품 복용률은 65%이지만, 
약물 상호작용 인지도는 12%에 불과하다.
이는 심각한 안전성 문제를 야기할 수 있어 해결이 필요하다.
"""
score1, reason1 = score_problem_definition(test1)
print(f"\n테스트 1: 짧지만 구체적인 문제 정의 ({len(test1)}자)")
print(f"  점수: {score1}/5")
print(f"  이유: {reason1}")
print(f"  ✅ 기대: 4-5점 (구체적 수치 포함)")

# 테스트 2: 긴데 내용 없는 문제 정의
test2 = """
저는 이번 프로젝트에서 데이터를 분석하고자 합니다.
데이터 분석은 매우 중요한 작업입니다.
많은 사람들이 데이터 분석에 관심을 가지고 있습니다.
데이터를 통해 많은 것을 알 수 있습니다.
이번 프로젝트를 통해 데이터 분석을 해보려고 합니다.
""" * 2  # 반복해서 길게
score2, reason2 = score_problem_definition(test2)
print(f"\n테스트 2: 길지만 내용 없는 문제 정의 ({len(test2)}자)")
print(f"  점수: {score2}/5")
print(f"  이유: {reason2}")
print(f"  ✅ 기대: 2-3점 (길이만 길고 내용 부족)")

# 테스트 3: 짧지만 깊이 있는 성찰
test3 = """
이번 프로젝트를 통해 데이터 분석의 한계를 깨달았다.
향후 더 많은 변수를 고려한 개선이 필요하다.
통계적 검증 방법을 배웠고, 앞으로 활용할 것이다.
"""
score3, reason3 = score_reflection(test3)
print(f"\n테스트 3: 짧지만 깊이 있는 성찰 ({len(test3)}자)")
print(f"  점수: {score3}/5")
print(f"  이유: {reason3}")
print(f"  ✅ 기대: 4-5점 (깊이 키워드 다수)")

# 테스트 4: 긴데 형식적인 성찰
test4 = """
이번 프로젝트는 정말 재미있었습니다.
좋은 경험이었고 즐거웠습니다.
흥미로운 내용이 많았고 신기했습니다.
다음에도 이런 프로젝트를 하고 싶습니다.
""" * 3  # 반복
score4, reason4 = score_reflection(test4)
print(f"\n테스트 4: 길지만 형식적인 성찰 ({len(test4)}자)")
print(f"  점수: {score4}/5")
print(f"  이유: {reason4}")
print(f"  ✅ 기대: 2-3점 (형식적 소감 패널티)")

print("\n" + "="*80)
print("v4 개선 효과:")
print("  ✅ 짧아도 내용 있으면 고득점")
print("  ✅ 길어도 내용 없으면 낮은 점수")
print("  ✅ 깊이 있는 성찰에 높은 점수")
print("  ✅ 형식적 소감에 패널티")
print("="*80)
