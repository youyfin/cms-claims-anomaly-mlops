# Data notes and caveats

Primary source: CMS 2008-2010 Data Entrepreneurs' Synthetic Public Use File (DE-SynPUF).

Official CMS pages:
- https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files
- https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf

The project uses inpatient claims fields including `DESYNPUF_ID`, `CLM_ID`, `CLM_FROM_DT`, `CLM_THRU_DT`, `PRVDR_NUM`, and `CLM_PMT_AMT`.

## Important interpretation caveat

DE-SynPUF is synthetic and was created for training, application development, and familiarity with CMS claims structures. It should **not** be used to make reliable inferential claims about real Medicare beneficiaries or real provider fraud prevalence.

This repository therefore frames the unsupervised model as an **anomaly-screening / investigation-prioritization prototype**, not as a fraud detector. A provider flagged by the model is not evidence of fraud.

The supervised high-cost claim task is included to demonstrate standard classification workflow and evaluation metrics. `is_high_cost_claim` is a derived educational target, not an adjudicated FWA label.
