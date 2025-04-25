# 🗂️ PyWBS - Project Task Management System

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-success?logo=django)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite&logoColor=white)](https://sqlite.org)

## 🔍 소개

**PyWBS**는 프로젝트 관리와 WBS(Task 기반 관리)를 지원하는 Django 기반 웹 애플리케이션입니다.  
프로젝트 생성, 업무(Task) 등록, 댓글 및 상태 관리까지 지원하며 Gantt 차트 시각화도 포함됩니다.

---

## 🎯 주요 기능

- 📁 프로젝트 등록 / 편집 / 삭제
- ✅ 태스크(Task) 등록 / 확인 / 삭제 / 우선순위
- 💬 댓글 관리 기능
- 👤 사용자 인증 (회원가입, 로그인)
- 📊 Gantt 차트 시각화 (JavaScript 기반)

---

## 📁 프로젝트 구조

```
📁 PyWBS/
├── wbs/               # 메인 앱: 프로젝트/태스크/댓글
│   ├── models/        # base.py, project.py, task.py 등
│   ├── forms/         # 프로젝트/태스크/댓글 폼
│   ├── templates/     # WBS 관련 템플릿 (task_card, project_list 등)
│   ├── static/wbs/    # Gantt 차트 JavaScript
│   ├── urls/          # 앱 라우팅 구성
│   └── views.py       # 전체 비즈니스 로직
│
├── config/            # Django 설정
├── templates/         # 로그인, 회원가입 폼
├── db.sqlite3
├── manage.py
└── requirements.txt
```

---

## 🚀 실행 방법

### 1. 환경 설정

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 마이그레이션 및 서버 실행

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

접속: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🖼️ 주요 화면

- 📌 프로젝트 대시보드
- 📌 태스크 카드 & 상세 페이지
- 📌 Gantt 차트 시각화
- 📌 댓글 관리 페이지

> 📷 스크린샷은 `/wbs/templates/wbs/` 및 `/media/` 디렉토리 참고

---


<p align="center"><i>Made with ❤️ by Django + JavaScript</i></p>
