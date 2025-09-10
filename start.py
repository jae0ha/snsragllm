"""
간단한 시작 스크립트
OpenAI API 키 설정 없이도 프로젝트 구조를 확인할 수 있습니다.
"""

import sys
import os
import yaml

def check_config():
    """설정 파일 확인"""
    print("🔍 설정 파일 확인 중...")
    
    if not os.path.exists('config.yaml'):
        print("❌ config.yaml 파일을 찾을 수 없습니다.")
        return False
    
    try:
        with open('config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        api_key = config.get('openai', {}).get('api_key', '')
        if api_key == 'your-openai-api-key-here' or not api_key:
            print("⚠️  OpenAI API 키가 설정되지 않았습니다.")
            print("   config.yaml 파일에서 api_key를 설정하거나")
            print("   .env 파일을 만들어 OPENAI_API_KEY를 설정하세요.")
            return False
        
        print("✅ 설정 파일이 올바르게 구성되었습니다.")
        return True
        
    except Exception as e:
        print(f"❌ 설정 파일 읽기 오류: {e}")
        return False

def check_dependencies():
    """필수 의존성 확인"""
    print("\n📦 필수 패키지 확인 중...")
    
    required_packages = [
        'streamlit',
        'fastapi', 
        'openai',
        'pydantic',
        'yaml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'yaml':
                import yaml
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  누락된 패키지: {', '.join(missing_packages)}")
        print("다음 명령어로 설치하세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✅ 모든 필수 패키지가 설치되었습니다.")
    return True

def show_project_info():
    """프로젝트 정보 표시"""
    print("\n" + "="*60)
    print("🚀 SNS & 네이버맵 리뷰 콘텐츠 생성기")
    print("="*60)
    
    print("\n📁 프로젝트 구조:")
    print("├── app.py                    # Streamlit 웹 애플리케이션")
    print("├── api.py                    # FastAPI REST API 서버")
    print("├── config.yaml               # 설정 파일")
    print("├── content_generator/        # 콘텐츠 생성 모듈")
    print("│   ├── sns_generator.py      # SNS 콘텐츠 생성기")
    print("│   └── review_generator.py   # 리뷰 생성기")
    print("└── tests/                    # 테스트 코드")
    
    print("\n🎯 주요 기능:")
    print("• 인스타그램, 페이스북, 트위터 게시물 생성")
    print("• 네이버맵, 구글 리뷰 생성")
    print("• 블로그 포스트 생성")
    print("• 일괄 콘텐츠 생성 (A/B 테스트용)")
    print("• RESTful API 제공")
    
    print("\n🚀 실행 방법:")
    print("1. Streamlit 웹 앱: streamlit run app.py")
    print("2. FastAPI 서버: python api.py")
    print("3. 테스트: python tests/test_api.py")

def main():
    """메인 함수"""
    print("🔄 프로젝트 초기화 확인 중...")
    
    # 의존성 확인
    deps_ok = check_dependencies()
    
    # 설정 확인
    config_ok = check_config()
    
    # 프로젝트 정보 표시
    show_project_info()
    
    if deps_ok and config_ok:
        print("\n✅ 모든 준비가 완료되었습니다!")
        print("\n다음 명령어로 앱을 실행하세요:")
        print("streamlit run app.py")
    elif deps_ok:
        print("\n⚠️  의존성은 설치되었지만 OpenAI API 키를 설정해야 합니다.")
        print("설정 없이도 프로젝트 구조는 확인할 수 있습니다:")
        print("streamlit run app.py")
    else:
        print("\n❌ 추가 설정이 필요합니다. 위의 지침을 따라주세요.")

if __name__ == "__main__":
    main()
