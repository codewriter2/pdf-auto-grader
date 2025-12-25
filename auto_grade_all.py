"""
DL 프로젝트 최종 보고서 자동 채점 스크립트 (v3)
- PDF 보고서 일괄 처리
- 루브릭 v3 적용

사용법:
    python auto_grade_all.py [폴더명]
    
예시:
    python auto_grade_all.py 10_report
    python auto_grade_all.py 05_report
"""
import pdfplumber
import re
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

def extract_sections(full_text):
    """전체 텍스트에서 각 섹션 추출"""
    sections = {}
    
    # 1. 문제 정의
    pattern1 = r'1\.\s*문제\s*정의.*?(?=2\.|$)'
    match1 = re.search(pattern1, full_text, re.DOTALL | re.IGNORECASE)
    if match1:
        sections['problem'] = match1.group(0)[:1000]
    else:
        pattern_alt = r'주제\s*[:：].*?(?=\n\n|2\.|1\.|$)'
        match_alt = re.search(pattern_alt, full_text, re.DOTALL)
        sections['problem'] = match_alt.group(0)[:500] if match_alt else ""
    
    # 2. 데이터
    pattern2 = r'2\.\s*.*?데이터.*?(?=3\.|$)'
    match2 = re.search(pattern2, full_text, re.DOTALL | re.IGNORECASE)
    sections['data'] = match2.group(0)[:1500] if match2 else ""
    
    # 3. 알고리즘
    pattern3 = r'3\.\s*.*?(알고리즘|코드|파이썬).*?(?=4\.|$)'
    match3 = re.search(pattern3, full_text, re.DOTALL | re.IGNORECASE)
    sections['algorithm'] = match3.group(0)[:1500] if match3 else ""
    
    # 4. 결과/시각화
    pattern4 = r'4\.\s*.*?결과.*?(?=5\.|6\.|$)'
    match4 = re.search(pattern4, full_text, re.DOTALL | re.IGNORECASE)
    sections['visualization'] = match4.group(0)[:1500] if match4 else ""
    
    # 5. 자아성찰
    pattern5 = r'[56]\.\s*.*?(성찰|소감).*?(?=7\.|동료평가|$)'
    match5 = re.search(pattern5, full_text, re.DOTALL | re.IGNORECASE)
    sections['reflection'] = match5.group(0)[:1500] if match5 else ""
    
    return sections


def score_problem_definition(text):
    """항목 1: 문제 정의 점수 (개선: 내용 중심 평가)"""
    if not text:
        return 1, "문제 정의 섹션 없음"
    
    text_length = len(text.strip())
    
    # 최소 길이 체크 (너무 짧으면 낮은 점수)
    if text_length < 20:
        return 1, f"너무 짧음 ({text_length}자)"
    elif text_length < 50:
        return 2, f"매우 짧음 ({text_length}자)"
    
    # 이후는 키워드와 구조 중심 평가
    problem_keywords = ["한계", "문제점", "부족", "어렵다", "그치다", "못한다", "못하다", "어려움", "문제"]
    background_keywords = ["기존", "현재", "대부분", "일반적", "많은", "전통적", "기존의"]
    solution_keywords = ["위해", "통해", "목표", "해결", "개선", "제안", "방안"]
    data_keywords = ["데이터", "통계", "조사", "연구", "분석"]
    
    problem_count = sum(1 for kw in problem_keywords if kw in text)
    background_count = sum(1 for kw in background_keywords if kw in text)
    solution_count = sum(1 for kw in solution_keywords if kw in text)
    has_data = any(kw in text for kw in data_keywords)
    has_numbers = bool(re.search(r'\d+%|\d+명|\d+건|\d+개', text))
    
    # 문장 구조 분석
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
    meaningful_sentences = len(sentences)
    
    criteria_met = 0
    
    # 1. 문제점 명확성 (가장 중요) - 최대 3점
    if problem_count >= 2: criteria_met += 3
    elif problem_count >= 1: criteria_met += 2
    
    # 2. 배경 설명 - 최대 2점
    if background_count >= 2: criteria_met += 2
    elif background_count >= 1: criteria_met += 1
    
    # 3. 해결 방향 제시 - 최대 2점
    if solution_count >= 2: criteria_met += 2
    elif solution_count >= 1: criteria_met += 1
    
    # 4. 구체성 (데이터/수치) - 최대 2점
    if has_numbers: criteria_met += 1
    if has_data: criteria_met += 1
    
    # 5. 문장 구조 (보너스) - 최대 1점
    if meaningful_sentences >= 3: criteria_met += 1
    
    # 점수 매핑 (총 10점 만점 → 5점 척도)
    if criteria_met >= 8: score = 5
    elif criteria_met >= 6: score = 4
    elif criteria_met >= 4: score = 3
    elif criteria_met >= 2: score = 2
    else: score = 2
    
    reason = f"{text_length}자/문제:{problem_count}/배경:{background_count}/해결:{solution_count}/구체성:{has_numbers or has_data}"
    return score, reason


def score_data_collection(text):
    """항목 2: 데이터 수집 및 설명 점수"""
    if not text:
        return 1, "데이터 섹션 없음"
    
    url_pattern = r'https?://[^\s\)>]+'
    urls = re.findall(url_pattern, text)
    has_url = len(urls) > 0
    
    source_keywords = ["data.go.kr", "KOSIS", "kosis", "통계청", "공공데이터", "국가통계포털"]
    has_source_name = any(kw in text for kw in source_keywords)
    
    dataset_keywords = ["데이터", "DB", "정보", "통계", "자료"]
    has_dataset_name = False
    for line in text.split('\n'):
        if any(kw in line for kw in dataset_keywords) and len(line.strip()) > 15:
            has_dataset_name = True
            break
    
    column_keywords = ["컬럼", "열", "항목", "필드", "변수", "칼로리", "인구", "유병률", "매출", "추출"]
    column_count = sum(1 for kw in column_keywords if kw in text)
    has_column_description = column_count >= 2
    
    processing_keywords = ["정규표현식", "계산", "전처리", "가공", "변환", "인덱싱", "매칭"]
    processing_count = sum(1 for kw in processing_keywords if kw in text)
    has_processing = processing_count >= 1
    
    criteria_met = 0
    if has_url: criteria_met += 2
    elif has_source_name: criteria_met += 1
    if has_dataset_name: criteria_met += 1
    if has_column_description: criteria_met += 1
    if has_processing: criteria_met += 1
    
    if criteria_met >= 4: score = 5
    elif criteria_met >= 3: score = 4
    elif criteria_met >= 2: score = 3
    elif criteria_met >= 1: score = 2
    else: score = 1
    
    reason = f"URL:{len(urls)}/출처:{has_source_name}/데이터명:{has_dataset_name}/컬럼:{has_column_description}"
    return score, reason


def score_algorithm(section3_text, full_text):
    """항목 3: 알고리즘 및 코드 점수 (v3 - 전체 텍스트 검색 지원)"""
    # 섹션 3이 있고 충분히 길면 섹션 3 사용, 아니면 전체 텍스트 사용
    text_to_analyze = section3_text if (section3_text and len(section3_text.strip()) > 50) else full_text
    is_full_text = (text_to_analyze == full_text)
    
    if not text_to_analyze:
        return 1, "알고리즘 섹션 없음"
    
    text_length = len(text_to_analyze.strip())
    
    # 함수명 패턴
    function_pattern = r'\w+\(\)'
    functions = re.findall(function_pattern, text_to_analyze)
    has_function_names = len(functions) > 0
    
    # 알고리즘 키워드
    algo_keywords = ["함수", "알고리즘", "로직", "계산", "처리", "구현", "방식", 
                     "그래프", "시각화", "분석"]
    algo_count = sum(1 for kw in algo_keywords if kw in text_to_analyze)
    
    # 라이브러리 키워드
    lib_keywords = ["matplotlib", "pandas", "numpy", "라이브러리", "맷플롯립", "판다스"]
    lib_count = sum(1 for kw in lib_keywords if kw in text_to_analyze)
    
    # 구체적 설명 키워드
    detail_keywords = ["상대오차", "패널티", "점수화", "최적화", "효율", "변수", 
                       "파라미터", "막대그래프", "히트맵", "네트워크"]
    detail_count = sum(1 for kw in detail_keywords if kw in text_to_analyze)
    
    criteria_met = 0
    
    # 길이 또는 키워드 개수
    if is_full_text:
        if algo_count >= 5: criteria_met += 2
        elif algo_count >= 3: criteria_met += 1
    else:
        if text_length >= 300: criteria_met += 2
        elif text_length >= 150: criteria_met += 1
    
    if has_function_names: criteria_met += 2
    if algo_count >= 3: criteria_met += 1
    if detail_count >= 2: criteria_met += 1
    if lib_count >= 1 and algo_count >= 2: criteria_met += 1
    
    if criteria_met >= 5: score = 5
    elif criteria_met >= 3: score = 4
    elif criteria_met >= 2: score = 3
    elif lib_count >= 1 or algo_count >= 1: score = 2
    else: score = 1
    
    source = "전체" if is_full_text else "섹션3"
    reason = f"{source}/{text_length}자/함수:{len(functions)}/알고:{algo_count}/라이브러리:{lib_count}"
    return score, reason


def score_visualization(text, page_count):
    """항목 4: 시각화 점수"""
    if not text:
        return 1, "시각화 섹션 없음"
    
    viz_types = ["막대그래프", "선그래프", "히트맵", "네트워크", "산점도", "파이차트", 
                 "boxplot", "그래프", "차트"]
    viz_count = sum(1 for kw in viz_types if kw in text)
    
    analysis_keywords = ["분석", "인사이트", "패턴", "경향", "상관관계", "비교", "확인", "결과"]
    analysis_count = sum(1 for kw in analysis_keywords if kw in text)
    
    advanced_viz = ["히트맵", "네트워크", "전후 비교", "산점도"]
    has_advanced = any(kw in text for kw in advanced_viz)
    
    criteria_met = 0
    if viz_count >= 3: criteria_met += 2
    elif viz_count >= 1: criteria_met += 1
    
    if analysis_count >= 3: criteria_met += 2
    elif analysis_count >= 1: criteria_met += 1
    
    if has_advanced: criteria_met += 1
    if page_count >= 5: criteria_met += 1
    
    if criteria_met >= 5: score = 5
    elif criteria_met >= 3: score = 4
    elif criteria_met >= 2: score = 3
    else: score = 2
    
    reason = f"시각화:{viz_count}/분석:{analysis_count}/고급:{has_advanced}/페이지:{page_count}"
    return score, reason


def score_reflection(text):
    """항목 5: 자아성찰 점수 (개선: 깊이 중심 평가)"""
    if not text:
        return 1, "성찰 섹션 없음"
    
    text_length = len(text.strip())
    
    # 최소 길이 체크
    if text_length < 20:
        return 1, f"너무 짧음 ({text_length}자)"
    elif text_length < 50:
        return 2, f"매우 짧음 ({text_length}자)"
    
    # 깊이 있는 성찰 키워드 (가중치 높음)
    deep_keywords = ["한계", "아쉬움", "개선", "향후", "과제", "깨달음", "성과", "의의", "부족", 
                     "배웠다", "느꼈다", "생각한다", "필요하다"]
    learning_keywords = ["배움", "학습", "이해", "알게", "깨달", "인식"]
    future_keywords = ["향후", "앞으로", "다음", "개선", "발전", "보완"]
    
    # 형식적 소감 (가중치 낮음)
    shallow_keywords = ["경험", "재미", "좋았다", "즐거웠다", "흥미", "신기"]
    
    deep_count = sum(1 for kw in deep_keywords if kw in text)
    learning_count = sum(1 for kw in learning_keywords if kw in text)
    future_count = sum(1 for kw in future_keywords if kw in text)
    shallow_count = sum(1 for kw in shallow_keywords if kw in text)
    
    # 문장 구조 분석
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
    meaningful_sentences = len(sentences)
    
    criteria_met = 0
    
    # 1. 깊이 있는 성찰 (가장 중요) - 최대 4점
    if deep_count >= 3: criteria_met += 4
    elif deep_count >= 2: criteria_met += 3
    elif deep_count >= 1: criteria_met += 2
    
    # 2. 학습 내용 언급 - 최대 2점
    if learning_count >= 2: criteria_met += 2
    elif learning_count >= 1: criteria_met += 1
    
    # 3. 향후 계획/개선 방향 - 최대 2점
    if future_count >= 2: criteria_met += 2
    elif future_count >= 1: criteria_met += 1
    
    # 4. 문장 구조 (보너스) - 최대 1점
    if meaningful_sentences >= 3: criteria_met += 1
    
    # 5. 형식적 소감 패널티
    if shallow_count > deep_count and shallow_count >= 2:
        criteria_met -= 2  # 형식적 소감만 많으면 감점
    
    # 점수 매핑 (총 9점 만점 → 5점 척도)
    if criteria_met >= 7: score = 5
    elif criteria_met >= 5: score = 4
    elif criteria_met >= 3: score = 3
    elif criteria_met >= 1: score = 2
    else: score = 2
    
    reason = f"{text_length}자/깊이:{deep_count}/학습:{learning_count}/향후:{future_count}/형식:{shallow_count}"
    return score, reason


def get_grade(total_score):
    """총점으로 등급 계산"""
    if total_score >= 23: return "A+"
    elif total_score >= 20: return "A"
    elif total_score >= 17: return "B+"
    elif total_score >= 14: return "B"
    elif total_score >= 11: return "C"
    else: return "D"


def extract_student_info(filename):
    """파일명에서 학생 정보 추출"""
    # 예: 김건우2025054_92284_4178699_DL_기말보고서(pythoneers_김건우).pdf
    match = re.match(r'([가-힣]+)(\d+)_.*?\.pdf', filename)
    if match:
        name = match.group(1)
        student_id = match.group(2)
        return name, student_id
    return filename, ""



# 메인 처리
if __name__ == "__main__":
    # 명령줄 인자로 폴더명 받기
    if len(sys.argv) < 2:
        print("사용법: python auto_grade_all.py [폴더명]")
        print("예시: python auto_grade_all.py 10_report")
        sys.exit(1)
    
    folder_name = sys.argv[1]
    PDF_FOLDER = rf"c:\exam\pdf_project\{folder_name}"
    
    # 폴더 존재 확인
    if not Path(PDF_FOLDER).exists():
        print(f"❌ 오류: 폴더를 찾을 수 없습니다: {PDF_FOLDER}")
        sys.exit(1)
    
    print("="*100)
    print("DL 프로젝트 최종 보고서 자동 채점 (v3)")
    print("="*100)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"PDF 폴더: {PDF_FOLDER}")
    
    # PDF 파일 목록
    pdf_files = list(Path(PDF_FOLDER).glob("*.pdf"))
    print(f"\n총 {len(pdf_files)}개 PDF 파일 발견")
    
    if len(pdf_files) == 0:
        print(f"❌ 오류: {PDF_FOLDER}에 PDF 파일이 없습니다.")
        sys.exit(1)

    # 결과 저장용 리스트
    results = []
    
    # 각 PDF 처리
    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"\n{'='*100}")
        print(f"[{idx}/{len(pdf_files)}] {pdf_path.name}")
        print(f"{'='*100}")
        
        try:
            # 학생 정보 추출
            student_name, student_id = extract_student_info(pdf_path.name)
            
            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""
                
                print(f"학생: {student_name} ({student_id})")
                print(f"페이지: {page_count}, 텍스트: {len(full_text)}자")
                
                # 섹션 추출
                sections = extract_sections(full_text)
                
                # 각 항목 채점
                scores = {}
                reasons = {}
                
                scores[1], reasons[1] = score_problem_definition(sections.get('problem', ''))
                scores[2], reasons[2] = score_data_collection(sections.get('data', ''))
                scores[3], reasons[3] = score_algorithm(sections.get('algorithm', ''), full_text)
                scores[4], reasons[4] = score_visualization(sections.get('visualization', ''), page_count)
                scores[5], reasons[5] = score_reflection(sections.get('reflection', ''))
                
                total_score = sum(scores.values())
                grade = get_grade(total_score)
                
                # 결과 출력
                print(f"\n📊 채점 결과:")
                print(f"  1. 문제 정의: {scores[1]}/5 - {reasons[1]}")
                print(f"  2. 데이터 수집: {scores[2]}/5 - {reasons[2]}")
                print(f"  3. 알고리즘: {scores[3]}/5 - {reasons[3]}")
                print(f"  4. 시각화: {scores[4]}/5 - {reasons[4]}")
                print(f"  5. 자아성찰: {scores[5]}/5 - {reasons[5]}")
                print(f"\n  ⭐ 총점: {total_score}/25")
                print(f"  📝 등급: {grade}")
                
                # 결과 저장
                results.append({
                    '순번': idx,
                    '파일명': pdf_path.name,
                    '학생명': student_name,
                    '학번': student_id,
                    '페이지수': page_count,
                    '문제정의': scores[1],
                    '데이터수집': scores[2],
                    '알고리즘': scores[3],
                    '시각화': scores[4],
                    '자아성찰': scores[5],
                    '총점': total_score,
                    '등급': grade,
                    '문제정의_상세': reasons[1],
                    '데이터수집_상세': reasons[2],
                    '알고리즘_상세': reasons[3],
                    '시각화_상세': reasons[4],
                    '자아성찰_상세': reasons[5]
                })
        
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            results.append({
                '순번': idx,
                '파일명': pdf_path.name,
                '학생명': student_name if 'student_name' in locals() else '오류',
                '학번': student_id if 'student_id' in locals() else '',
                '페이지수': 0,
                '문제정의': 0,
                '데이터수집': 0,
                '알고리즘': 0,
                '시각화': 0,
                '자아성찰': 0,
                '총점': 0,
                '등급': 'F',
                '문제정의_상세': str(e),
                '데이터수집_상세': '',
                '알고리즘_상세': '',
                '시각화_상세': '',
                '자아성찰_상세': ''
            })

    # 결과를 DataFrame으로 변환
    df = pd.DataFrame(results)
    
    # 통계 출력
    print(f"\n{'='*100}")
    print("📊 전체 통계")
    print(f"{'='*100}")
    print(f"총 처리: {len(results)}개")
    print(f"\n등급 분포:")
    grade_counts = df['등급'].value_counts().sort_index()
    for grade, count in grade_counts.items():
        print(f"  {grade}: {count}개")
    
    print(f"\n평균 점수:")
    print(f"  문제 정의: {df['문제정의'].mean():.2f}/5")
    print(f"  데이터 수집: {df['데이터수집'].mean():.2f}/5")
    print(f"  알고리즘: {df['알고리즘'].mean():.2f}/5")
    print(f"  시각화: {df['시각화'].mean():.2f}/5")
    print(f"  자아성찰: {df['자아성찰'].mean():.2f}/5")
    print(f"  총점: {df['총점'].mean():.2f}/25")
    
    # CSV 저장
    output_csv = rf"c:\exam\pdf_project\{folder_name}_결과.csv"
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n✅ 결과 저장: {output_csv}")
    
    # Excel 저장
    output_excel = rf"c:\exam\pdf_project\{folder_name}_결과.xlsx"
    df.to_excel(output_excel, index=False, engine='openpyxl')
    print(f"✅ 결과 저장: {output_excel}")
    
    print(f"\n종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
