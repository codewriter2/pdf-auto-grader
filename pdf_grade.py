import pdfplumber
import os
import re
import pandas as pd
from pathlib import Path
import sys

def extract_text_from_pdf(pdf_path):
    text = ""
    num_pages = 0
    num_images = 0
    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            for page in pdf.pages:
                # 텍스트 추출
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                # 이미지 개수 합산
                num_images += len(page.images)
    except Exception as e:
        # 암호 걸린 파일이거나 손상된 파일일 경우
        print(f"[Warning] Error reading {pdf_path.name}: {e}")
        return None, 0, 0
    return text, num_pages, num_images

def get_top_keywords(text, n=5):
    # 간단한 불용어 리스트
    stopwords = {"문제", "정의", "과정", "결과", "결론", "대해", "통해", "위해", "하는", "있다", "없다", "것이다", "경우", "가장", "매우", "분석", "데이터", "사용", "이용"}
    
    words = re.findall(r'[가-힣a-zA-Z]{2,}', text) # 2글자 이상 단어만
    counts = {}
    for w in words:
        if w not in stopwords:
            counts[w] = counts.get(w, 0) + 1
            
    # 빈도수 순 정렬
    sorted_words = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [w for w, c in sorted_words[:n]]

def extract_section(text, start_keywords, end_keywords_list):
    # 텍스트 내에서 start_keywords 중 하나가 처음 나오는 위치 찾기
    start_idx = -1
    for k in start_keywords:
        idx = text.find(k)
        if idx != -1:
            start_idx = idx
            break
            
    if start_idx == -1: return ""
    
    # 그 이후에 end_keywords 중 하나가 나오는 위치 찾기
    sub_text = text[start_idx:] 
    end_idx = len(sub_text)
    
    for k_list in end_keywords_list: # 여러 후보군 중 가장 먼저 나오는 것
        for k in k_list:
            idx = sub_text.find(k)
            # 자기 자신(제목) 바로 뒤에 나오는 경우 방지 (최소 20자 뒤)
            if idx > 20: 
                end_idx = min(end_idx, idx)
                
    return sub_text[:end_idx]

def grade_pdf_report(file_path):
    file_path = Path(file_path)
    # 점수 초기화 (5점 만점 기준)
    scores = {
        "Def(1.0)": 0.0,
        "Process(1.0)": 0.0,
        "Result(1.0)": 0.0,
        "Visual(1.5)": 0.0,
        "Reflection(0.5)": 0.0,
        "Total(5.0)": 0.0
    }
    comments = []
    
    # 1. 파일 확인
    ext = file_path.suffix.lower()
    if ext != '.pdf':
        return scores, [f"지원하지 않는 파일 형식({ext})"], ""
    
    # 2. 내용 추출
    full_text, num_pages, num_images = extract_text_from_pdf(file_path)
    if full_text is None:
        return scores, ["PDF 읽기 실패"], ""
        
    # 섹션 정의 키워드
    keys_def = ["문제 정의", "주제", "목표", "선정 동기"]
    keys_proc = ["해결 과정", "데이터 수집", "분석 방법", "알고리즘", "설계"]
    keys_res = ["결과", "결론", "인사이트", "성과"]
    keys_ref = ["소감", "느낀점", "성찰", "후기"]
    
    # 3. 섹션별 텍스트 추출 (대략적 분리)
    # 문제정의 ~ (해결과정 or 결과 or 소감) 전까지
    text_def = extract_section(full_text, keys_def, [keys_proc, keys_res, keys_ref])
    # 해결과정 ~ (결과 or 소감) 전까지
    text_proc = extract_section(full_text, keys_proc, [keys_res, keys_ref])
    # 결과 ~ (소감) 전까지
    text_res = extract_section(full_text, keys_res, [keys_ref])
    
    full_text_lower = full_text.lower()

    # --- (1) 문제 정의 평가 및 핵심 주제어 추출 ---
    top_topics = []
    if text_def and len(text_def) > 50: # 내용이 어느 정도 있어야 함
        scores["Def(1.0)"] = 1.0
        # 주제어 추출 (문제 정의 섹션에서 가장 많이 쓴 단어)
        top_topics = get_top_keywords(text_def, n=3)
        # comments.append(f"핵심 주제어: {', '.join(top_topics)}")
    elif text_def:
        scores["Def(1.0)"] = 0.5
        comments.append("문제 정의 내용 빈약")
    else:
        comments.append("문제 정의 섹션 미발견")

    # --- (2) 해결 과정 평가 (주제 일관성 체크) ---
    if text_proc and len(text_proc) > 50:
        # 기술적 키워드 체크
        tech_terms = ["전처리", "수집", "분석", "라이브러리", "시각화", "학습", "모델", "알고리즘"]
        has_tech = any(t in text_proc for t in tech_terms)
        
        # 주제 일관성 체크: 문제 정의에서 뽑은 키워드가 여기서도 언급되는가?
        relevance = 0
        if top_topics:
            relevance = sum(1 for t in top_topics if t in text_proc)
            
        if has_tech and (not top_topics or relevance > 0):
            scores["Process(1.0)"] = 1.0
        elif has_tech:
            scores["Process(1.0)"] = 0.5
            comments.append(f"해결 과정이 주제({', '.join(top_topics)})와 연관성 낮음")
        else:
            scores["Process(1.0)"] = 0.5
            comments.append("해결 과정 기술적 서술 부족")
    elif text_proc:
         scores["Process(1.0)"] = 0.5
         comments.append("해결 과정 빈약")
    else:
        comments.append("해결 과정 섹션 미발견")
        
    # --- (3) 결과 도출 평가 (주제 일관성 & 논리 체크) ---
    if text_res and len(text_res) > 50:
        ins_terms = ["확인", "나타", "보여", "증가", "감소", "따라서", "결과"]
        has_ins = any(t in text_res for t in ins_terms)
        
        relevance = 0
        if top_topics:
            relevance = sum(1 for t in top_topics if t in text_res)

        if has_ins and (not top_topics or relevance > 0):
            scores["Result(1.0)"] = 1.0
        elif has_ins:
             scores["Result(1.0)"] = 0.5
             comments.append(f"결과가 초기 주제({', '.join(top_topics)})와 연관성 낮음")
        else:
             scores["Result(1.0)"] = 0.5
             comments.append("단순 결과 나열(분석 부족)")
    elif text_res:
        scores["Result(1.0)"] = 0.5
        comments.append("결과 내용 빈약")
    else:
        comments.append("결과 섹션 미발견")

    # (4) 시각화 (1.5)
    if num_images >= 3:
        scores["Visual(1.5)"] = 1.5
    elif num_images >= 1:
        scores["Visual(1.5)"] = 1.0
        comments.append(f"이미지 부족({num_images})")
    else:
        comments.append("이미지 없음")
        
    # (5) 소감 (0.5)
    if any(k in full_text for k in keys_ref):
        scores["Reflection(0.5)"] = 0.5
    else:
        comments.append("소감 미발견")

    # [New] 요약 정보 생성 (Top Keywords)
    # 전체 텍스트에서 빈도 높은 단어 추출
    all_top_keywords = get_top_keywords(full_text, n=5)
    summary_str = ", ".join([f"{w}({full_text.count(w)})" for w in all_top_keywords])

    # 총점
    scores["Total(5.0)"] = sum(scores.values())
    
    return scores, comments, summary_str

def grade_pdf_folder(folder_path_str):
    folder_path = Path(folder_path_str)
    
    # 결과 저장용 리스트
    results = []
    
    print(f"Scanning folder: {folder_path}")
    
    # 모든 파일 순회
    for file_path in folder_path.iterdir():
        if file_path.is_file():
            filename = file_path.name
            
            # 간단한 이름 추출
            name_match = re.match(r'^([가-힣]+)', filename)
            student_name = name_match.group(1) if name_match else filename[:5]
            
            print(f"Grading: {filename} ...")
            
            # 함수 호출 시 summary_str도 반환받음
            scores, comments, summary_str = grade_pdf_report(file_path)
            
            # 결과 행 생성
            row = {
                "file_name": filename,
                "student_name": student_name,
                "Summary": summary_str, # 요약 추가
                **scores,
                "comments": " / ".join(comments) if comments else "양호"
            }
            results.append(row)
            
    # DataFrame 생성 및 저장
    if not results:
        print("채점할 파일이 없습니다.")
        return
        
    df = pd.DataFrame(results)
    
    # 컬럼 순서 정렬
    cols = ["student_name", "Total(5.0)", "Def(1.0)", "Process(1.0)", "Result(1.0)", "Visual(1.5)", "Reflection(0.5)", "Summary", "comments", "file_name"]
    # 실제 존재하는 컬럼만 선택
    existing_cols = [c for c in cols if c in df.columns]
    df = df[existing_cols]
    
    output_dir = folder_path.parent
    folder_name = folder_path.name
    csv_path = output_dir / f"{folder_name}_보고서결과.csv"
    xlsx_path = output_dir / f"{folder_name}_보고서결과.xlsx"
    
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False)
    
    print("\n=== 채점 완료 ===")
    print(f"저장 위치:\n - {csv_path}\n - {xlsx_path}")
    print("\nPreview:")
    print(df[["student_name", "Total(5.0)", "Summary"]].head())

if __name__ == "__main__":
    print("=== PDF 보고서 채점 프로그램 ===")
    target = input("채점할 폴더 경로를 입력하세요 (예: c:\\exam\\pdf_project\\10): ").strip()
    
    if target and os.path.exists(target):
        grade_pdf_folder(target)
    else:
        print("경로가 유효하지 않습니다.")
