# Khurram's AI — School Tutor

A Streamlit school-study assistant for Classes 1–10, with extra focus on Classes 9 and 10. It includes subject, board, language, and explanation-style settings.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, and `README.md` to the repository root.
3. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
4. Create an app, choose your repository and branch, and set the main file path to `app.py`.
5. Deploy.

The default configuration does not require an API token. It attempts to use a public third-party AI endpoint, which can be rate-limited, unavailable, or subject to changing terms. Therefore, this setup does **not** guarantee unlimited or permanently free AI responses.

## Optional: Hugging Face token

If you later want to use Hugging Face Inference instead, add a token in your Streamlit app's **Settings → Secrets** (do not commit secrets to GitHub):

```toml
HF_TOKEN = "your_hugging_face_token"
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"
```

The model/provider may require access or billing depending on current Hugging Face terms and available inference providers.

## Important limitations

- This app does not include a verified database of all current Pakistani textbooks or board syllabi.
- AI-generated answers can be wrong; students should verify important work with a teacher or textbook.
- Do not submit passwords, private information, or sensitive personal data to the app.
- This is a responsive website, not a published Android/iOS app. It may be possible to use the deployed site as an installable shortcut, depending on the browser/device.
