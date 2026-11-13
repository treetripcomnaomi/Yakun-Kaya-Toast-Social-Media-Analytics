# A Heritage-Led Rejuvenation Strategy for Ya Kun Kaya Toast

NMC5342 Social Media Analytics, Group 2, National University of Singapore (2026)
JIANG Jingyi, KONG Shuting, LU Chenyue, LU Lingzhi, YAO Xinyan

> **📓 [Open the analysis notebook](NMC5342_Group%202%20Yakun_notebook.ipynb)** · **📁 [Browse all files](https://github.com/YOUR-USERNAME/YaKun_NMC5342_analysis)**

This repository contains the code and analysis behind our final report. The report designs a data-informed social media strategy for Ya Kun Kaya Toast, a Singapore heritage brand that wants to reach younger audiences.

## Research questions

| RQ | Question | Report section |
|---|---|---|
| RQ1 | On Ya Kun's own channels, does heritage or novelty content perform better? | §5 (Step 3) |
| RQ2 | How do users talk about Ya Kun's heritage, and do they value it? | §6 (Step 4) |
| RQ3 | How do competitors use heritage, and how does Ya Kun compare? | §7 (Step 5) |
| RQ4 | How does Ya Kun's heritage content perform on youth-skewed platforms? | §8 |

Sections 3 to 7 and 11 follow the six steps of the course brief (audit, audience, what works, social listening, competitive analysis, content strategy).

## Repository structure

```
├── README.md
├── NMC5342_Group 2 Yakun_notebook.ipynb   main notebook, executed, with all outputs and report figures
├── analysis_outputs/                       aggregate results and charts (charts_1103/)
└── scripts/                                collection, cleaning and analysis helpers
```

**Start with the [notebook](NMC5342_Group%202%20Yakun_notebook.ipynb).** Each section heading names the report section it supports, e.g. "5 Step 1: social media audit (report §3)". Section 12 of the notebook checks the numbers in the notebook against the numbers in the report.

## Data

We collected 11,733 public items and analysed 7,317 after removing duplicates and irrelevant content.

| Source | Content | Tool |
|---|---|---|
| Instagram | Official posts of Ya Kun and three competitors, plus comments | Apify |
| TikTok | Official videos, and user videos about Ya Kun and kaya toast | Apify |
| YouTube | Videos and comments about Ya Kun | YouTube Data API v3 |
| Xiaohongshu | Notes about Ya Kun | Apify |
| Reddit | Posts and comments about Ya Kun | Apify |
| Brand24 | Web and social mentions | Brand24 |

Competitors: Toast Box (direct), Old Chang Kee (indirect), % Arabica (aspirational).

**Raw data are not included.** The scraped files contain the usernames and posts of ordinary social media users. To protect their privacy and respect platform terms, this public repository shares the code, the executed notebook (with all outputs) and aggregate results only. Raw and cleaned data are available to the course instructor on request.

## Methods in brief

- **LLM coding with human validation.** Claude coded all posts against our codebook. Two human coders validated each code on stratified samples (fixed seed 5342). The acceptance threshold was Cohen's κ ≥ 0.60, with Gwet's AC1 also checked.
- **Sentiment.** LLM coding was cross-checked with Twitter-RoBERTa (`cardiffnlp/twitter-roberta-base-sentiment`, Barbieri et al., 2020). Lexicons (VADER, TextBlob, AFINN) and classifiers trained on LLM labels were compared against human coders.
- **Heritage axis.** A semantic axis in pretrained word2vec space (GoogleNews vectors), learned with logistic regression from LLM labels. It was evaluated by AUC on 112 human-agreed posts, which were excluded from training.
- **Topics.** NMF on TF-IDF features of user posts.
- **Tests.** Mann–Whitney U, Kruskal–Wallis and chi-square tests, and OLS regression with HC3 robust standard errors. All results are correlational.

## Reproducing the analysis

Re-running requires the raw data (see above). The notebook already shows every output, so it can be read without running it.

```bash
pip install -r requirements.txt
jupyter notebook "NMC5342_Group 2 Yakun_notebook.ipynb"
```

Large pretrained models (the `models/` folder) are not stored here because of GitHub's file-size limit. Download them separately:

- Twitter-RoBERTa sentiment model: `cardiffnlp/twitter-roberta-base-sentiment` on Hugging Face
- word2vec GoogleNews vectors (300 dimensions)

API keys are never stored in the code. `scripts/youtube_collect.py` reads the YouTube key from the environment variable `YT_API_KEY`, or asks for it at run time.

## Use of AI

Claude (Anthropic) was used to code posts against the codebook, with human validation as described above, and to assist with code. All coding decisions, reliability checks and interpretations were reviewed by the group.
