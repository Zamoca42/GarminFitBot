# GarminFitBot

Garmin 기기의 건강 데이터를 AI로 분석하여 더 나은 건강 관리를 도와주는 카카오톡 챗봇 서비스입니다.

## 배경 및 문제 정의

Garmin 스마트워치는 뛰어난 정확도와 다양한 건강 데이터를 제공하지만, 이 데이터를 더 효과적으로 활용할 수 있는 방법이 필요합니다.

### 기존 도구의 한계와 개선 기회

#### GarminDB

- **비동기 처리의 필요성**: 수집, 분석 프로세스에 도메인별로 처리하느라 최소 40분 소요
- **데이터 변환 과정 간소화 가능성**: JSON→파일→SQLite 변환 과정을 간소화하여 사용성 향상
- **사용자 친화적 인터페이스 개발 기회**: CLI 명령어 대신 직관적인 인터페이스로 접근성 개선

#### GarminConnect 앱

- **더 풍부한 피드백 제공 가능성**: 모닝 리포트 외에도 다양한 맥락에서 통찰력 제공
- **데이터 시각화 개선 기회**:
  - 더 통합적이고 한눈에 파악하기 쉬운 인터페이스 구현
  - 개인화된 분석으로 데이터의 실질적 가치 향상
  - AI 기반 심층 분석으로 유의미한 인사이트 제공

GarminFitBot은 이러한 개선 기회를 포착하여 AI 기술로 Garmin 데이터를 수집하고 분석하며, 사용자에게 더 가치 있는 건강 인사이트를 제공합니다.

## 서비스 링크

- 🏠 [웹사이트](https://garmin-fit-bot.vercel.app/)
- 📚 [API 문서](https://api.fit-bot.click)
- 💬 [카카오톡 채널](https://pf.kakao.com/_GVxmnn)

## 주요 기능

- Garmin Connect 계정 연동
- 건강 데이터 자동 수집 (심박수, 스트레스, 활동량, 수면, 활동 데이터)
- AI 기반 건강 상태 분석
- 카카오톡을 통한 편리한 인터페이스

## 사용 방법

1. [카카오톡 채널 추가하기](https://pf.kakao.com/_GVxmnn)
2. Garmin Connect 계정 연동
3. "데이터 수집해줘" 명령어로 건강 데이터 수집
4. 건강 관련 질문으로 AI 분석 결과 확인
   - 예시: "요즘 내가 잠을 잘 자고 있나?"
   - AI가 수집된 수면 데이터를 분석하여 수면 품질과 개선점을 알려드립니다

## 데모

### 데이터 수집

<div style="display: flex; gap: 1rem; justify-content: center;">
  <img src="https://raw.githubusercontent.com/zamoca42/GarminFitBot/main/frontend/src/lib/images/screenshots/chatbot-collect-fit-data.png" alt="데이터 수집 데모" width="45%"/>
  <img src="https://raw.githubusercontent.com/zamoca42/GarminFitBot/main/frontend/src/lib/images/screenshots/result-collect-fit-data.png" alt="데이터 수집 결과" width="45%"/>
</div>

### AI 분석

<div style="display: flex; gap: 1rem; justify-content: center;">
  <img src="https://raw.githubusercontent.com/zamoca42/GarminFitBot/main/frontend/src/lib/images/screenshots/chatbot-analysis-health.png" alt="AI 분석 요청" width="45%"/>
  <img src="https://raw.githubusercontent.com/zamoca42/GarminFitBot/main/frontend/src/lib/images/screenshots/result-analysis-health.png" alt="AI 분석 결과" width="45%"/>
</div>

## 프로젝트 타임라인

![](https://raw.githubusercontent.com/zamoca42/GarminFitBot/main/project-timeline.png)
[노션 페이지에서 보기](https://zamoca.notion.site/GarminFitBot-1c79bb5b026280149917e3ab601b6448)

## ERD

<img src="https://mermaid.ink/svg/pako:eNrVWMFu2zgQ_RWBpy3gBl7ZShzdtg2KLhYFFknaQ2GAYMSxTJgiBYpy4k3z7x1KtiPZlOW0DrrNwZE1j8OZx8chx48k0RxITMBcCZYalk1VgH-fCzDBt29v3-rH4CMwY6-ZhSsm5CqIgzkr9lE31kBR9EAg70FIgPwG_QitujB_JVYshW35qD93At0N_xoYFyrFcYlWlgm1HtyMvJVM94BtHs3M_lbWMM5W-_hmVs1MP-klZKDs8SM-Xn_piqrB1GP97P7eiRTjghTfCh78-8-zBXNEN3-EUfQmgAyzCT53WLkocslWVLEM_IhZKeWO-RYebKBZaefU6gWobgstIDFgO-bWGJry2xZswTRNpEAKqeCNGUQGhWVZHqBjXHlOmfVZy5y3rE8H1HQUpw1LiQuBQQUfGuYr9Ba4KZ9fbeCoN4uJ0bnZt2Xswf9eKO97tmz7OS0dG_35CeGOLFqUWcbMilb0DHYpcDM2QmkxuLVjSMZSi49U6oTJXlSa2X0q5i5qalqUH5lwsyy88uK7BSuq6aiEJUi_BA4j1lZeYrJYNdym0ooXfqUdgJ1ELO36-Vsoxc_u0fluT4RXlorVlkmUAs63b0z1vu2D1EgclnDLVOJxiIRpI8DjjbmDFihWmdL67DOptSlc_c3ugJ9cQc0T9X-toC0AFD_KXM3hU2Br4TYn3fBNvRJ45ena-wL_qwIBL6e5edF4JemejMDdZfoBjtfbp6s2cmSDFrL67MJIkc5tH8hA1gdh92wBB8ydZ0K9o-tDftkxMNehbwC6y0Vd-T1npVnSe4AF7inE-u2S4eGhKgaOwUS0uqPg856uI9S1Q-Oi2rLwX_CcfQbA71iy8M91xwqQQrn1vqdlnoPpwd0x6eogdwOOhe74relsQbEALXAvLJks4dSFsNUo-LfoRmnVNv71R6krR2bp235dhewlXDRaoN-CDSeUTmEcTHfb6Z6iMDe23XYV7CrvqdOlTX6yEPs9dNXpvttK__X2wH3GVUxPP9Bqszz25_JZ5NC86GwGAqq5jipt9ar1QLzCCOVaO5jNILEnLg-3kOXvqw741vXSTanUKx5s-2O_fOEBTwQoOuZ-YWRkQDIw2LFzEpMqlCmxcyxdUxLjo4IS2ZBTMlUOykqrb1YqIbE1JQyI0WU6J_GMyQK_1c7Xv0ptIDlTX7XefgUurDaf6p-wql-yKgiJH8kDicNheDa5vJhcjqPocjIMhxcDsiLx-ehsFIWjcDQeRuej8Wj8NCD_VU6HZ5NwEoXj8Z_Di3B8PrqcDEhqXDLrAFG2YN7rUln0Hj59Bw2NH7I" alt="ERD" width="80%">

[Mermaid 에디터에서 ERD 보기](https://mermaid.live/edit#pako:eNrVWE1v4zYQ_SsCT13ACfwlx9Gtu8Fii2KBIsn2UBggGHEsE6ZIgaKcuNn89w4l25FsynK2DtrNwZE1j8OZx8chx88k1hxIRMDcCJYYls5UgH_fcjDB9-8XF_o5-ALM2Ftm4YYJuQ6iYMHyQ9SdNZDnHRDIOhASILtDP0KrNsyvsRUrYRs-qs-9QPfDvwXGhUpwXKyVZUJtBtcjbyTTPmCXRz2z35Q1jLP1Ib6eVT3Tr3oFKSh7-ogvt3-2RVVj6rl6dn8fRYJxQYJvBQ_--P3Vgjmim1-GYfghgBSzCb61WLnIM8nWVLEU_Ih5IeWe-R6ebKBZYRfU6iWodgvNITZgW-bWGJry25ZsyTSNpUAKqeC1GUQKuWVpFqBjXHlOmfVZi4w3rC9H1HQSpzVLgQuBQQWfa-Yb9Ba4KV9fbeGoN4uJ0YU5tKXsyf9eKO97tmr6OS8dW_35CeGOLJoXacrMmpb09PYpcDPWQmkwuLNjSMZSi49U6pjJTlSS2kMqFi5qahqUn5hwvSy88-K7BcvL6aiEFUi_BI4jNlZeYLJYNdym0ornfqUdgZ1FLM36-VMoxc_uyfnuToR3lorVlkmUAs53aEz0oe2z1EgclnDLVOxxiIRpI8DjjbmDFihWmcL67HOptcld_U0fgJ9dQfUT9X-toB0AFD_JXM7hU2Bj4bYnXf9DtRJ45Wnb-wL_qxwBb6e5ftF4J-mejcD9ZfoBjjfbp602cmSD5rL8bMNIkSxsF8hA2gVhj2wJR8ytZ0K1o6tDftUyMNND3wB0l4mq8nvOSrOijwBL3FOI9dslw8NDlQycgglpeUfB5wNdh6hrh8ZFtUXuv-A5-xyAP7B46Z_rgeUghXLr_UiLLAPTgXtg0tVB7gacCt3zW9HZgGIBWuJeWDFZwLkLYaNR8G_RrdLKbfzfH6WuHJmVb_u1FbK3cFFrgX4KNpxQWoVxNN1dp3uOwlzbdrtVsOuso04XNv6Xhdjvoa1Od91Wuq-3R-4zrmJ6-oFGm-Wxv5bPPIP6RWc7EFDNVVRJo1etBuIVRijX2sF8DrE9c3m4hzT7VHbA966XrkulWvFg1x_75QtPeCJA3jL3GyMjPZKCwY6dk4iUocyIXWDpmpEIHznMWSHtjMyUg7LC6ru1iklkTQE9YnSRLEg0ZzLHb5Xzza9SW0jG1F9a774CF1abr9VPWOUvWSWERM_kiUSD_vByPL0eXV-FV8OwP-2Pe2RNooury8loPB4Mw9FkNJig-aVH_i699i-vp6P-9XgQhlfT6Xg4mPRIYlw2mwhRt2A-6UJZEk0nL_8AFTcf3Q)

## 데이터 흐름도

### 인증 및 챗봇 서비스 연결

<img src="https://mermaid.ink/svg/pako:eNp9lG1v0lAUx7_KzX21JWzDAhv0xRIn0RhjNJm-MSTkht5BM2ixD-pclgytGPegWyKGISwszm0mGJExZck-Eff2O3h6C4wFkBC4bX_n9Jz_eVjHKV2hWMYmfW5TLUXjKkkbJJfQEHxIytIN9NSkBiIm4m8avPKDH-75D_PEsNSUmieahR6QVaIL5rLtfcvHbvEIsfb7UfT24_seeJeYlnfkTpW1nDGYbWWEw1qHn9QEdunwreNR8om-SjUPdYt1t9D8Hxpf8ji22-S1tus0WasOh7HkPWLkVOG1d4JYfcr_9TSZWVwUecvIrezwr3vd5iY_fId45TNv_fQx8Rw4sJbRHIGc5la9W3OmmtbsPHLLHf6n6rPAeCQwMsoQTcnSpGCTPjs13cMAAC6-JCN-6PDtKnILbVa78jL50nG3OgMd3ta483vIqB9HKqtSzUqqCmLNsntQvn79hIzYacEtNBCvO2y7MZwY8J4QE3FePBojmgjihoX7seyFf7oJRvu8uDsqyAtqqCtrST_0qUEGkzXxNei2NqF7fCi-NDNw15eoWncrZ6AScg9K0GmTgoUw2a8rxI6q3b8d4CDMEjtvw191bPl6FaM5omYD0Fem-VI3lACaELfoYKiLQYlFk2nRcP1Ue6RAAPW7UUaPxHz00xjqOB-YufZ6g2TNarfzYdjliCRDRR6WtT_716lD5b6jqZ6Z-6nhls6mx3QbqNs9v4A53mfbFzdazW-d_tQcOOzbDuKlHXZyhQM4Rw1QT4HNtO4ZJbCVoTmawDIcNWpbBskmcELbABTGSl9e01JYtgybBrCh2-kMlldI1oQrO6-Aqr211kdgxp_p-uCSKiosuof-JhQLUSBYXsevsCwFpdlobCEaC0cisWhQCi4E8BqW50OzoYgUkkLhYGQ-FA6FNwL4tXAanI1K0YgUDt8KLkjh-VAsFsBpw0umFyDVFGrc0W3NAu-RyMY_on1GJA" alt="인증 데이터 흐름도" width="80%">

[Mermaid 에디터에서 인증 흐름도 보기](https://mermaid.live/edit#pako:eNp9lG1v0lAUx7_KzX21JWzDAhv0xRIn0RhjNJm-MSTkht5BM2ixD-pclgytGPegWyKGISwszm0mGJExZck-Eff2O3h6C4wFkBC4bX_n9Jz_eVjHKV2hWMYmfW5TLUXjKkkbJJfQEHxIytIN9NSkBiIm4m8avPKDH-75D_PEsNSUmieahR6QVaIL5rLtfcvHbvEIsfb7UfT24_seeJeYlnfkTpW1nDGYbWWEw1qHn9QEdunwreNR8om-SjUPdYt1t9D8Hxpf8ji22-S1tus0WasOh7HkPWLkVOG1d4JYfcr_9TSZWVwUecvIrezwr3vd5iY_fId45TNv_fQx8Rw4sJbRHIGc5la9W3OmmtbsPHLLHf6n6rPAeCQwMsoQTcnSpGCTPjs13cMAAC6-JCN-6PDtKnILbVa78jL50nG3OgMd3ta483vIqB9HKqtSzUqqCmLNsntQvn79hIzYacEtNBCvO2y7MZwY8J4QE3FePBojmgjihoX7seyFf7oJRvu8uDsqyAtqqCtrST_0qUEGkzXxNei2NqF7fCi-NDNw15eoWncrZ6AScg9K0GmTgoUw2a8rxI6q3b8d4CDMEjtvw191bPl6FaM5omYD0Fem-VI3lACaELfoYKiLQYlFk2nRcP1Ue6RAAPW7UUaPxHz00xjqOB-YufZ6g2TNarfzYdjliCRDRR6WtT_716lD5b6jqZ6Z-6nhls6mx3QbqNs9v4A53mfbFzdazW-d_tQcOOzbDuKlHXZyhQM4Rw1QT4HNtO4ZJbCVoTmawDIcNWpbBskmcELbABTGSl9e01JYtgybBrCh2-kMlldI1oQrO6-Aqr211kdgxp_p-uCSKiosuof-JhQLUSBYXsevsCwFpdlobCEaC0cisWhQCi4E8BqW50OzoYgUkkLhYGQ-FA6FNwL4tXAanI1K0YgUDt8KLkjh-VAsFsBpw0umFyDVFGrc0W3NAu-RyMY_on1GJA)

### 데이터 수집

<img src="https://mermaid.ink/svg/pako:eNqNlV1rGkEUhv_KMFcJGKPr914EmkhLKYVC25siyKCTZMm6a3fHUhsCTZXUJilpQEFTEwxNsQELktpi6D_Kzv6Hntn1q1lNFJFx9znnvPPOzJltnNGzFMvYpK8LVMvQpEI2DJJLaQg-JMN0A700qYGIifiHDj-55Gdf3Jd5YjAlo-SJxtATskV0h7nuiW_9wt47R1bvoxd98OyxAB8Sk4khLzetq7IXe0HMLcHZpSbfv7B3OyLQi61RlRpFAQ5G_Osh_3sxBdRVlTrTAdb63OWnPbvcRbxS5-1jR8V1GQp5A5Or_0VYVy0YTCUfESOnaIIejEaK3V_h49LKiuOVPEXDSZVf_XRRhwEWMshomYEXyxl3Asiu9_mfpovBa4CEVTJSNIUphNH0AFR0bWHRxQQAnOuQjAZAel1h6SxhxJ-lKikuZFSFaiytZH0IntJBrBsE0clVebwDEG_VrF89xM-79smhSyZXlyaKeNAFe69l73aRfdSxaz8WJ40Z1XB9A2_aFd5-b7U_IeuocdPv2o0q4gfNm24Z2Y0aP-27cS4-WXWM26X3_EysqF3q2NXyneX4Qcfq1mAZJhdlYjW8daZE3Mo92m9jvzcpbJa0Ad4OF2YEDf2dJqQFE_l-t_5K3brszS_-Fn6_clOlND9TtKf6HIphXfb7VqsCg_l1Tw2aQz0zqGnOlD9Dyv2TsBtN2G9zy7-N3y8c2q_yBk41nSneK2GW7GEzGfdT3ihb3w4RL-3Cs3E_GXeoYV8acKfH1sHvyfYEpGhpMkphbzNzglIYWZdVOLlwmrEP56iRI0oWbpttkSeF2SbN0RQWGTRaYAZRUzil7QBKCkx_XtQyWGZGgfqwoRc2NrG8TlQT_hXyokMNrqrRU2jCr3Q9NwyhWQWMeupeb84t5yBY3sZvsRyMRPyhWDwcDUnBgBSKhX24iOVQ0C9FpHggIoUTiWggmNjx4XdOzoA_Hg8notFYKBiIBcMxSfLhDUNMZiCQallqrOkFjUEaaecf6zUcog" alt="수집 데이터 흐름도" width="80%">

[Mermaid 에디터에서 데이터 수집 흐름도 보기](https://mermaid.live/edit#pako:eNqNlV1rGkEUhv_KMFcJGKPr914EmkhLKYVC25siyKCTZMm6a3fHUhsCTZXUJilpQEFTEwxNsQELktpi6D_Kzv6Hntn1q1lNFJFx9znnvPPOzJltnNGzFMvYpK8LVMvQpEI2DJJLaQg-JMN0A700qYGIifiHDj-55Gdf3Jd5YjAlo-SJxtATskV0h7nuiW_9wt47R1bvoxd98OyxAB8Sk4khLzetq7IXe0HMLcHZpSbfv7B3OyLQi61RlRpFAQ5G_Osh_3sxBdRVlTrTAdb63OWnPbvcRbxS5-1jR8V1GQp5A5Or_0VYVy0YTCUfESOnaIIejEaK3V_h49LKiuOVPEXDSZVf_XRRhwEWMshomYEXyxl3Asiu9_mfpovBa4CEVTJSNIUphNH0AFR0bWHRxQQAnOuQjAZAel1h6SxhxJ-lKikuZFSFaiytZH0IntJBrBsE0clVebwDEG_VrF89xM-79smhSyZXlyaKeNAFe69l73aRfdSxaz8WJ40Z1XB9A2_aFd5-b7U_IeuocdPv2o0q4gfNm24Z2Y0aP-27cS4-WXWM26X3_EysqF3q2NXyneX4Qcfq1mAZJhdlYjW8daZE3Mo92m9jvzcpbJa0Ad4OF2YEDf2dJqQFE_l-t_5K3brszS_-Fn6_clOlND9TtKf6HIphXfb7VqsCg_l1Tw2aQz0zqGnOlD9Dyv2TsBtN2G9zy7-N3y8c2q_yBk41nSneK2GW7GEzGfdT3ihb3w4RL-3Cs3E_GXeoYV8acKfH1sHvyfYEpGhpMkphbzNzglIYWZdVOLlwmrEP56iRI0oWbpttkSeF2SbN0RQWGTRaYAZRUzil7QBKCkx_XtQyWGZGgfqwoRc2NrG8TlQT_hXyokMNrqrRU2jCr3Q9NwyhWQWMeupeb84t5yBY3sZvsRyMRPyhWDwcDUnBgBSKhX24iOVQ0C9FpHggIoUTiWggmNjx4XdOzoA_Hg8notFYKBiIBcMxSfLhDUNMZiCQallqrOkFjUEaaecf6zUcog)

### 데이터 분석

<img src="https://mermaid.ink/svg/pako:eNp9lf1rE0kYx_-VYX6qsMa8tWkX9LCGAzkUUe8XCYQhGdOlm924O3saS0HretczFRWMxF4iUYtayA-x3Ypy-g9lZv8Hn9nZbdYmGsK-fp637zzP7Aau2XWKdezSWx61arRskIZDmhULwY_UmO2gP13qIOIisTUSu_vi1VP1skUcZtSMFrEY-oOsEztivgTy39sL_36NePDPLHr-ykUJ_k5cJi-F3-cH_ix2nbjrkgsf9MWjvfD-SBrOYheoSZ22BOMr8d-O-H9vTtgGhSNwV-n5Wnw7J6ptm66k-Cdf-APEn_iTo9EsV16NoMdjMQhCf8wPhnABeSpSHaVsp8-di6TR0eRjMBl3pyZJBPF-m48-K4vLNqPI_osqyTUUm1aweH-Pb_WRePsV8a0Aie0e3w9QuPMh9AMxuIfEi4B3h3D8rYLTKUQOIAeQTkdnGEh6hljEbLsGCNv7LD71FQfvgZKS6ygC7tLqGiUmW6vWCSMLpxQmAeCU0jEJrhIUGshpZ-rUJO2FmmmAwFWjrqHo8al0WsoBeCqv6tOuQmLY5YdQ3etxuLujyPLq6VTAKXqxjPi4F77szXUbLS7kJ08Zx7MWohQ05IGqkNIPuUTs1EYtx_Hyj5-gyaEf7j6ONH_3bZ5l1DM6alBWdU1KW0qyOJaGmNGkN2Gi6NkKNqHpq7cpXa_gRFJpnCihlnXaIrNKxLFmyMnBeHL4Ne0yVdKwG_a64cvn_Gl_xvIXBSWNoIpqEcaoYy1MSzxRQWylmvK4u7d74Yt_5-cVI-nU5y_J4BnvHCHxYCD8j2ki3RlHffHmYYL-tDWSUZgTWo7AdFqTmEOfd0bpWQJEzubP51n5RHz_uej0YW5PTnbkRkPKyY-T3fkiOrCP9E7Otx_7DrsBzAfvbGcymQrGGm5Sp0mMOuzeGzJMBbM12qQVLB1b1GMOMeV-sAko8Zh9rW3VsM4cj2rYsb3GGtZvEtOFO68FC5ps_cdPYae7YdvNxITWDfgaXFKfi-irESFY38B3sJ5bXMwUSsvFpUI-l80XSkUNt7FeyGXyi_nl7GK-uLKylM2tbGr4buQzm1leLq4sLZUKuWwpVyzl8xpuOLKYOEFq1alzwfYsBm6Km98BSMDAmw" alt="분석 데이터 흐름도" width="80%">

[Mermaid 에디터에서 데이터 분석 흐름도 보기](https://mermaid.live/edit#pako:eNp9lf1rE0kYx_-VYX6qsMa8tWkX9LCGAzkUUe8XCYQhGdOlm924O3saS0HretczFRWMxF4iUYtayA-x3Ypy-g9lZv8Hn9nZbdYmGsK-fp637zzP7Aau2XWKdezSWx61arRskIZDmhULwY_UmO2gP13qIOIisTUSu_vi1VP1skUcZtSMFrEY-oOsEztivgTy39sL_36NePDPLHr-ykUJ_k5cJi-F3-cH_ix2nbjrkgsf9MWjvfD-SBrOYheoSZ22BOMr8d-O-H9vTtgGhSNwV-n5Wnw7J6ptm66k-Cdf-APEn_iTo9EsV16NoMdjMQhCf8wPhnABeSpSHaVsp8-di6TR0eRjMBl3pyZJBPF-m48-K4vLNqPI_osqyTUUm1aweH-Pb_WRePsV8a0Aie0e3w9QuPMh9AMxuIfEi4B3h3D8rYLTKUQOIAeQTkdnGEh6hljEbLsGCNv7LD71FQfvgZKS6ygC7tLqGiUmW6vWCSMLpxQmAeCU0jEJrhIUGshpZ-rUJO2FmmmAwFWjrqHo8al0WsoBeCqv6tOuQmLY5YdQ3etxuLujyPLq6VTAKXqxjPi4F77szXUbLS7kJ08Zx7MWohQ05IGqkNIPuUTs1EYtx_Hyj5-gyaEf7j6ONH_3bZ5l1DM6alBWdU1KW0qyOJaGmNGkN2Gi6NkKNqHpq7cpXa_gRFJpnCihlnXaIrNKxLFmyMnBeHL4Ne0yVdKwG_a64cvn_Gl_xvIXBSWNoIpqEcaoYy1MSzxRQWylmvK4u7d74Yt_5-cVI-nU5y_J4BnvHCHxYCD8j2ki3RlHffHmYYL-tDWSUZgTWo7AdFqTmEOfd0bpWQJEzubP51n5RHz_uej0YW5PTnbkRkPKyY-T3fkiOrCP9E7Otx_7DrsBzAfvbGcymQrGGm5Sp0mMOuzeGzJMBbM12qQVLB1b1GMOMeV-sAko8Zh9rW3VsM4cj2rYsb3GGtZvEtOFO68FC5ps_cdPYae7YdvNxITWDfgaXFKfi-irESFY38B3sJ5bXMwUSsvFpUI-l80XSkUNt7FeyGXyi_nl7GK-uLKylM2tbGr4buQzm1leLq4sLZUKuWwpVyzl8xpuOLKYOEFq1alzwfYsBm6Km98BSMDAmw)

## LangGraph Agent Graph

![LangGraph Agent Graph](https://raw.githubusercontent.com/zamoca42/GarminFitBot/main/backend/agent_graph.png)

## 기술 스택

### Backend

- Python FastAPI
- Celery
- Redis
- PostgreSQL

### Frontend

- SvelteKit
- TailwindCSS

### Infrastructure

- Vercel (Frontend)
- AWS EC2, ECS, lambda (Backend)
- Prometheus

### AI/ML

- Langchain / Langgraph / Langsmith
- Google Gemini 2.0 flash

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
