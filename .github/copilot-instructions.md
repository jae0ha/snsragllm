<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created.

- [x] Clarify Project Requirements

- [x] Scaffold the Project

- [x] Customize the Project

- [x] Install Required Extensions

- [x] Compile the Project

- [x] Create and Run Task

- [x] Launch the Project

- [x] Ensure Documentation is Complete

## Project Summary

**SNS & 네이버맵 리뷰 콘텐츠 생성기** is a Python-based marketing automation tool that uses RAG (Retrieval-Augmented Generation) technology to generate advertising content for social media platforms and review sites.

### Key Features:
- **SNS Content Generation**: Instagram, Facebook, Twitter/X, and Blog posts
- **Review Generation**: Naver Map and Google Reviews
- **Batch Generation**: Multiple content versions for A/B testing
- **REST API**: FastAPI server for programmatic access
- **Web Interface**: Streamlit-based user-friendly interface

### Tech Stack:
- **Backend**: FastAPI, OpenAI GPT
- **Frontend**: Streamlit
- **Language Processing**: Korean and English support
- **Data Processing**: Pandas, NumPy, scikit-learn

### Usage:
1. **Web Interface**: Run `streamlit run app.py`
2. **API Server**: Run `python api.py`
3. **Setup Check**: Run `python start.py`

### Configuration:
- Set OpenAI API key in `config.yaml` or `.env` file
- Customize generation parameters in `config.yaml`
- Review ethical guidelines for responsible marketing

This tool is designed for marketing professionals who need to generate authentic, engaging content at scale while maintaining quality and compliance with platform policies.
