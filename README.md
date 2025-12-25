# PDF 프로젝트 자동 채점 시스템

학생들이 제출한 PDF 형식의 미니 프로젝트 보고서를 자동으로 채점하는 Python 기반 시스템입니다.

## 📋 프로젝트 개요

이 프로젝트는 학생들의 PDF 보고서를 분석하여 다음 항목들을 평가합니다:
- 문제 정의 (Problem Definition)
- 해결 과정 (Process)
- 결과 (Results)
- 시각화 (Visualization)
- 소감 (Reflection)

## 🚀 주요 기능

- **자동 PDF 분석**: PDF 파일에서 텍스트와 이미지를 추출하여 분석
- **섹션별 채점**: 각 섹션의 존재 여부와 내용의 질을 평가
- **일괄 처리**: 폴더 내 모든 PDF 파일을 한 번에 처리
- **결과 출력**: CSV 및 Excel 형식으로 채점 결과 저장

## 📦 필요 패키지

```bash
pip install PyPDF2 pandas openpyxl
```

## 💻 사용 방법

### 1. 단일 폴더 채점

```bash
python auto_grade_all.py <PDF_폴더_경로>
```

예시:
```bash
python auto_grade_all.py "10_report"
```

### 2. 스크립트 내에서 직접 실행

`auto_grade_all.py` 파일을 열어 `main()` 함수의 폴더 경로를 수정한 후 실행:

```bash
python auto_grade_all.py
```

## 📊 출력 결과

채점 결과는 다음 두 가지 형식으로 저장됩니다:
- `<폴더명>_결과.csv`: CSV 형식
- `<폴더명>_결과.xlsx`: Excel 형식

각 파일에는 다음 정보가 포함됩니다:
- 학생 이름
- 각 섹션별 점수
- 총점
- 학점 (A+, A, B+, B, C+, C, D+, D, F)

## 📝 채점 기준

상세한 채점 기준은 `rubric_final_v3.md` 파일을 참조하세요.

### 점수 배분 (총 30점)
- 문제 정의: 6점
- 해결 과정: 6점
- 결과: 6점
- 시각화: 9점
- 소감: 3점

### 학점 기준
- A+: 28점 이상
- A: 26점 이상
- B+: 24점 이상
- B: 22점 이상
- C+: 20점 이상
- C: 18점 이상
- D+: 16점 이상
- D: 14점 이상
- F: 14점 미만

## 📁 프로젝트 구조

```
pdf_project/
├── auto_grade_all.py       # 메인 채점 스크립트
├── pdf_grade.py            # PDF 채점 로직
├── rubric_final_v3.md      # 채점 기준 문서
├── test_v4_improvements.py # 테스트 스크립트
├── 10_report/              # 샘플 PDF 폴더
├── 11_report/              # 샘플 PDF 폴더
└── 5_report/               # 샘플 PDF 폴더
```

## 🔧 주요 파일 설명

### `auto_grade_all.py`
- 폴더 내 모든 PDF 파일을 일괄 처리
- 명령줄 인자로 폴더 경로 지정 가능
- 결과를 CSV와 Excel로 자동 저장

### `pdf_grade.py`
- PDF 파일 분석 및 채점 로직
- 섹션별 점수 계산
- 텍스트 및 이미지 추출

### `rubric_final_v3.md`
- 상세한 채점 기준 문서
- 각 섹션별 평가 항목
- 점수 배분 기준

## 🤝 기여

이슈나 개선 사항이 있으시면 언제든지 제안해주세요!

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.
