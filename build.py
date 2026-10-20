#!/usr/bin/env python3
"""src/<slug>.html 본문 조각을 layout.html로 감싸 docs/<slug>.html로 출력. stdlib만 사용.

    python3 build.py              # 빌드
    python3 -m http.server -d docs 8000   # 로컬 확인
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC, DOCS, STATIC = ROOT / "src", ROOT / "docs", ROOT / "static"

# 커리큘럼 = 목차. (장 제목, [(slug, 페이지 제목), ...]). src/에 파일이 없으면 회색으로만 표시.
TOC = [
    ("0. 인증의 기초", [("basics", "식별·인증·인가와 인증 요소"),
                        ("threats", "위협 모델 어휘")]),
    ("1. 패스워드", [("password-storage", "서버 저장: 해시·솔트·KDF"),
                     ("password-policy", "정책의 역사와 NIST SP 800-63B"),
                     ("password-guessing", "추측 모델 계보와 강도 추정"),
                     ("password-managers", "패스워드 관리자")]),
    ("2. OTP와 MFA", [("otp", "HOTP·TOTP와 공유 비밀"),
                      ("mfa", "푸시·SMS·MFA 피로, 그리고 MFA가 못 막는 것")]),
    ("3. 공개키 기반 인증", [("pki", "챌린지-응답과 PKI·인증서"),
                           ("npki", "공동인증서(구 공인인증서)"),
                           ("smartcard", "클라이언트 인증서·스마트카드·SSH 키")]),
    ("4. FIDO와 패스키", [("fido2", "U2F → FIDO2: WebAuthn + CTAP"),
                         ("passkeys", "패스키: synced vs device-bound"),
                         ("passkeys-vs-npki", "패스키 vs 공동인증서")]),
    ("5. 연합 인증과 SSO", [("idp", "IdP와 SSO 개념"),
                           ("kerberos", "Kerberos 인증 흐름"),
                           ("saml", "SAML 2.0"),
                           ("oauth-oidc", "OAuth 2.0 vs OIDC"),
                           ("tokens", "토큰·세션·쿠키"),
                           ("cloud-idp", "Entra ID·Okta와 AD")]),
    ("6. 생체 인증", [("biometrics", "로컬 매칭 vs 서버 매칭, FAR·FRR")]),
    ("7. 계정 등록·복구", [("recovery", "가장 약한 고리")]),
    ("8. 실전 공격 사례", [("attacks", "Kerberoasting부터 세션 탈취까지")]),
    ("9. 실습 랩", [("lab-webauthn", "WebAuthn 등록·인증 데모"),
                    ("lab-totp", "TOTP 생성기"),
                    ("lab-compare", "방식별 \"서버에 남는 것\" 비교")]),
]


def nav_html(current):
    out = []
    for chapter, pages in TOC:
        out.append(f'<li class="chap">{chapter}<ul>')
        for slug, title in pages:
            if not (SRC / f"{slug}.html").exists():
                out.append(f'<li class="todo">{title}</li>')
            elif slug == current:
                out.append(f'<li class="cur"><a href="{slug}.html">{title}</a></li>')
            else:
                out.append(f'<li><a href="{slug}.html">{title}</a></li>')
        out.append("</ul></li>")
    return "\n".join(out)


def main():
    titles = {slug: title for _, pages in TOC for slug, title in pages}
    layout = (ROOT / "layout.html").read_text()
    if DOCS.exists():
        shutil.rmtree(DOCS)
    shutil.copytree(STATIC, DOCS / "static")
    (DOCS / ".nojekyll").touch()
    for src in sorted(SRC.glob("*.html")):
        slug = src.stem
        title = "사용자 인증 연구소" if slug == "index" else titles[slug]
        body = src.read_text().replace("{{toc}}", nav_html(None))
        html = (layout.replace("{{title}}", title)
                      .replace("{{nav}}", nav_html(slug))
                      .replace("{{body}}", body))
        (DOCS / src.name).write_text(html)
        print("built", src.name)


if __name__ == "__main__":
    main()
