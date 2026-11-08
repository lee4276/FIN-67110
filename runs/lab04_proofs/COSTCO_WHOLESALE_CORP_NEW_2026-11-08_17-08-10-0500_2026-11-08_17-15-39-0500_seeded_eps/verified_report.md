Filings read: 10-K 0000909832-26-000093; 10-Q 0000909832-26-000051; 8-K 0000909832-26-000084; earnings release EX-99.1 from 8-K 0000909832-26-000084

## Automated verifier marks

Semantic line review: completed for model-returned cited lines; inspect the verifier node output.

| Claim | Mark | Code check and evidence | Correction from saved evidence |
|---|---|---|---|
| 1 | correct | Value matches saved facts or release after report rounding; 10-K 0000909832-26-000093, fiscal years ended 2026-08-30 and 2025-08-31; total revenue XBRL |  |
| 2 | correct | Value matches saved facts or release after report rounding; 10-K 0000909832-26-000093, fiscal years ended 2026-08-30 and 2025-08-31; (current / prior - 1) × 100 |  |
| 3 | correct | Value matches saved facts or release after report rounding; 10-K 0000909832-26-000093, fiscal years ended 2026-08-30 and 2025-08-31; operating income XBRL |  |
| 4 | correct | Value matches saved facts or release after report rounding; 10-K 0000909832-26-000093, fiscal years ended 2026-08-30 and 2025-08-31; net income XBRL |  |
| 5 | wrong | Reported 21.76 USD per diluted share; saved evidence gives 20.76 USD per diluted share; 10-K_0000909832-26-000093.txt:L749: NET INCOME PER COMMON SHARE:; 10-K_0000909832-26-000093.txt:L750: \| \| \| \| \|; 10-K_0000909832-26-000093.txt:L751: \| Basic \| $ \| 20.78 \| \| \| $ \| 18.24 \| \| \| $ \| 16.59 \|; 10-K_0000909832-26-000093.txt:L752: \| Diluted \| $ \| 20.76 \| \| \| $ \| 18.21 \| \| \| $ \| 16.56 \| | 20.76 USD per diluted share; 10-K 0000909832-26-000093, fiscal years ended 2026-08-30 and 2025-08-31; EarningsPerShareDiluted |
| 6 | correct | Value matches saved facts or release after report rounding; 10-K 0000909832-26-000093, fiscal years ended 2026-08-30 and 2025-08-31; net income / average equity × 100 |  |
| 7 | correct | Value matches saved facts or release after report rounding; 10-K 0000909832-26-000093, fiscal years ended 2026-08-30 and 2025-08-31; debt including current portion / equity × 100 |  |
| 8 | correct | Value matches saved facts or release after report rounding; 10-K 0000909832-26-000093, fiscal years ended 2026-08-30 and 2025-08-31; operating cash flow - property additions |  |
| 9 | correct | Value matches saved facts or release after report rounding; EX-99.1 0000909832-26-000084; line 53; quarter revenue |  |
| 10 | correct | Value matches saved facts or release after report rounding; EX-99.1 0000909832-26-000084; line 53; (current / prior - 1) × 100 |  |
| 11 | correct | Value matches saved facts or release after report rounding; EX-99.1 0000909832-26-000084; release narrative, latest quarter |  |
| peer-WMT-revenue | correct | Peer 10-K 0000104169-26-000055, year ended 2026-01-31; revenue Revenues, operating income OperatingIncomeLoss;  |  |
| peer-WMT-operating income | correct | Peer 10-K 0000104169-26-000055, year ended 2026-01-31; revenue Revenues, operating income OperatingIncomeLoss;  |  |
| peer-WMT-operating margin | correct | Peer 10-K 0000104169-26-000055, year ended 2026-01-31; revenue Revenues, operating income OperatingIncomeLoss;  |  |
| peer-TGT-revenue | correct | Peer 10-K 0000027419-26-000016, year ended 2026-01-31; revenue RevenueFromContractWithCustomerExcludingAssessedTax, operating income OperatingIncomeLoss;  |  |
| peer-TGT-operating income | correct | Peer 10-K 0000027419-26-000016, year ended 2026-01-31; revenue RevenueFromContractWithCustomerExcludingAssessedTax, operating income OperatingIncomeLoss;  |  |
| peer-TGT-operating margin | correct | Peer 10-K 0000027419-26-000016, year ended 2026-01-31; revenue RevenueFromContractWithCustomerExcludingAssessedTax, operating income OperatingIncomeLoss;  |  |
| peer-BJ-revenue | correct | Peer 10-K 0001531152-26-000007, year ended 2026-01-31; revenue RevenueFromContractWithCustomerExcludingAssessedTax, operating income OperatingIncomeLoss;  |  |
| peer-BJ-operating income | correct | Peer 10-K 0001531152-26-000007, year ended 2026-01-31; revenue RevenueFromContractWithCustomerExcludingAssessedTax, operating income OperatingIncomeLoss;  |  |
| peer-BJ-operating margin | correct | Peer 10-K 0001531152-26-000007, year ended 2026-01-31; revenue RevenueFromContractWithCustomerExcludingAssessedTax, operating income OperatingIncomeLoss;  |  |

Human audit and partner checks: pending; no human mark is implied.

Run time: 2026-11-08T17:08:10.090224-05:00

## Overview

Costco’s business model combines membership warehouses and e-commerce with low prices, a limited assortment, high sales volumes, and rapid inventory turnover. Management attributes its ability to operate at lower gross margins to purchasing and distribution efficiencies and no-frills facilities: “offering low prices on a limited selection” produces “high sales volumes and rapid inventory turnover” (`10-K_0000909832-26-000093.txt:L188`). Membership provides a recurring revenue component and reinforces loyalty; the format is designed to provide “continuing fee revenue” (`10-K_0000909832-26-000093.txt:L481`).

**Recent results show continued growth.** Fiscal 2026 net sales increased 10.1% to $297.2 billion, while fourth-quarter sales increased 11.2% to $93.9 billion (“fiscal year increased 10.1 percent”; “quarter increased 11.2 percent,” `EX-99.1_0000909832-26-000084.txt:L12`). Full-year net income reached $9.226 billion, or $20.76 per diluted share, versus $8.099 billion and $18.21 previously (“Net income for the fiscal year was $9.226 billion,” `EX-99.1_0000909832-26-000084.txt:L25`).

Membership economics also strengthened: fee revenue increased 11%, driven by sign-ups, fee increases, and Executive upgrades (“driven by new member sign-ups, membership fee increases, and upgrades,” `10-K_0000909832-26-000093.txt:L545`). However, the fee increase contributed approximately 30% of fiscal 2026 membership-income growth, so that growth should not be interpreted entirely as expansion in membership numbers (“approximately 30%,” `10-K_0000909832-26-000093.txt:L548`).

**Consistency check:** The net-sales figures above and the total-revenue figures below use different definitions, not conflicting measures. Total revenue includes net sales and membership fees. Accordingly, annual net-sales growth of 10.1% and quarterly net-sales growth of 11.2% should not be substituted for total-revenue growth of 10.14% and 11.10%, respectively (10-K accession **0000909832-26-000093**, L733–735; 8-K Exhibit 99.1 accession **0000909832-26-000084**, L42–53).

## Market Positioning and Growth Outlook

- **Competitive differentiation rests on value and operating efficiency.** Costco limits its core warehouse assortment to fewer than 4,000 active SKUs, supporting a focused merchandising model (“less than 4,000 active stock keeping units,” `10-K_0000909832-26-000093.txt:L195`). Kirkland Signature adds differentiation and, according to management, generally earns higher margins (“differentiate our merchandise offerings, and generally earn higher margins,” `10-K_0000909832-26-000093.txt:L249`). Nevertheless, competition spans major retailers and warehouse clubs, including Amazon, Walmart, Sam’s Club, and BJ’s (“Our industry is highly competitive,” `10-K_0000909832-26-000093.txt:L247`). The supplied evidence is insufficient to quantify market share or independently verify relative pricing superiority.

- **Membership loyalty supports the competitive position.** Renewal rates ended fiscal 2026 at 92.3% in the U.S. and Canada and 89.8% worldwide (“92.3% in the U.S. and Canada and 89.8% worldwide,” `10-K_0000909832-26-000093.txt:L223`). These are trailing measures rather than immediate retention readings: they capture renewals “seven to eighteen months prior to the reporting date” (`10-K_0000909832-26-000093.txt:L223`).

- **Existing locations and digital channels provide growth catalysts.** Fiscal 2026 comparable-sales growth reflected a 5% increase in average ticket and 3% growth in shopping frequency (“increases of 5% in average ticket and 3% in shopping frequency,” `10-K_0000909832-26-000093.txt:L536`). Digitally enabled comparable sales increased 21% on the rounded 10-K presentation (“increased 21% during 2026,” `10-K_0000909832-26-000093.txt:L537`). These results support monitoring digital engagement and repeat shopping as growth drivers, but do not establish a future growth rate.

- **Expansion offers opportunity with execution constraints.** Costco added 25 net warehouses in fiscal 2026 (“a total of 25 net new warehouses,” `10-K_0000909832-26-000093.txt:L490`). Management expects relatively faster square-footage growth in many international markets, but identifies lower initial profitability and cannibalization as drawbacks (“lower initial operating profitability”; “we expect that to continue,” `10-K_0000909832-26-000093.txt:L480`). The excerpts provide insufficient evidence for a quantified future opening schedule.

## Valuation Insights

| # | Claim and report figure with arithmetic | Period and definition | Filing evidence |
|---|---|---|---|
| 1 | **Annual total revenue: $303.154 billion**, versus prior-year revenue of **$275.235 billion**. | FY2026 ended 2026-08-30; prior FY2025 ended 2025-08-31. Total revenue includes net sales and membership fees. | 10-K, accession **0000909832-26-000093**, L733–735; XBRL `RevenueFromContractWithCustomerExcludingAssessedTax`, periods ended 2026-08-30 and 2025-08-31. |
| 2 | **Annual revenue growth: 10.14%**. Arithmetic: ($303.154 billion ÷ $275.235 billion − 1) × 100. | FY2026 ended 2026-08-30 versus FY2025 ended 2025-08-31; growth in total revenue, not net sales alone. | 10-K, accession **0000909832-26-000093**, L735; `RevenueFromContractWithCustomerExcludingAssessedTax`, periods ended 2026-08-30 and 2025-08-31. |
| 3 | **Annual operating income and margin: $11.685 billion and 3.85%**. Margin arithmetic: $11.685 billion ÷ $303.154 billion × 100. | FY2026 ended 2026-08-30; operating margin equals operating income divided by total revenue. | 10-K, accession **0000909832-26-000093**, L739 and L735; `OperatingIncomeLoss` and `RevenueFromContractWithCustomerExcludingAssessedTax`, period ended 2026-08-30. |
| 4 | **Annual net income attributable to company: $9.226 billion**. | FY2026 ended 2026-08-30; consolidated GAAP net income of Costco and its wholly owned subsidiaries. | 10-K, accession **0000909832-26-000093**, L747 and consolidation policy L932; `NetIncomeLoss`, period ended 2026-08-30. |
| 5 | **Annual GAAP diluted EPS: $20.76 per diluted share**. | FY2026 ended 2026-08-30; reported diluted net income per common share. | 10-K, accession **0000909832-26-000093**, L749–752; `EarningsPerShareDiluted`, period ended 2026-08-30. | Corrected source: saved filing line in mark table | <!-- Automated correction; see original report.md -->
| 6 | **Return on average equity: 28.40%**. Arithmetic: $9.226 billion ÷ [($35.803 billion + $29.164 billion) ÷ 2] × 100. | FY2026 ended 2026-08-30; annual net income divided by average equity at 2026-08-30 and 2025-08-31, rather than ending equity alone. | 10-K, accession **0000909832-26-000093**, L747 and L829; `NetIncomeLoss`, year ended 2026-08-30; `StockholdersEquity`, balances at 2026-08-30 and 2025-08-31. |
| 7 | **Debt to equity including current debt: 17.21%**. Arithmetic: ($3.914 billion + $2.248 billion) ÷ $35.803 billion × 100. | As of 2026-08-30; noncurrent long-term debt plus its current portion, divided by ending equity. This definition excludes lease liabilities. | 10-K, accession **0000909832-26-000093**, L808, L812 and L829; `LongTermDebtCurrent`, `LongTermDebtNoncurrent` and `StockholdersEquity`, balances at 2026-08-30. |
| 8 | **Free cash flow: $9.382 billion**. Arithmetic: $15.817 billion − $6.435 billion. | FY2026 ended 2026-08-30; calculated operating cash flow less additions to property and equipment, not a separate GAAP statement subtotal. | 10-K, accession **0000909832-26-000093**, L893 and L895; `NetCashProvidedByUsedInOperatingActivities` and `PaymentsToAcquirePropertyPlantAndEquipment`, period ended 2026-08-30. |
| 9 | **Latest-quarter total revenue: $95.723 billion**. | Fiscal Q4 FY2026, the 16 weeks ended 2026-08-30; total revenue includes net sales and membership fees. | 8-K Exhibit 99.1, accession **0000909832-26-000084**, L42–53, “Total revenue,” quarter ended 2026-08-30. |
| 10 | **Latest-quarter year-over-year total revenue growth: 11.10%**. Arithmetic: ($95.723 billion ÷ $86.156 billion − 1) × 100. | Fiscal Q4 FY2026 ended 2026-08-30 versus fiscal Q4 FY2025 ended 2025-08-31; compares the corresponding 16-week quarters, not sequential quarters or net sales alone. | 8-K Exhibit 99.1, accession **0000909832-26-000084**, L44–53, “Total revenue,” quarters ended 2026-08-30 and 2025-08-31. |
| 11 | **Latest-quarter GAAP diluted EPS: $6.75 per diluted share**. | Fiscal Q4 FY2026, the 16 weeks ended 2026-08-30; reported GAAP diluted EPS, without adjusting out nonrecurring items. | 8-K Exhibit 99.1, accession **0000909832-26-000084**, L25 and L68–71, “Diluted,” quarter ended 2026-08-30. |

**Historical P/E:** **43.18×**, calculated as the supplied **$896.48 per-share price dated 2026-09-24** divided by **$20.76 FY2026 GAAP diluted EPS**. Price source: assigned `price_and_date`; EPS source: 10-K accession **0000909832-26-000093**, L752, fiscal year ended **2026-08-30**. This is a dated historical earnings multiple, not a forward multiple or price target.

**Peer operating comparison.** Fiscal years can differ across companies; the periods below are each peer’s own supplied fiscal year and are not aligned with Costco’s August year-end. Operating margin is operating income divided by total revenue.

| Peer | Own fiscal-year period | Total revenue | Operating income | Operating margin and arithmetic | Filing evidence |
|---|---|---|---|---|---|
| Walmart (WMT) | 2025-02-01 to 2026-01-31 | $713.163 billion | $29.825 billion | **4.18%** = $29.825 billion ÷ $713.163 billion × 100 | 10-K accession **0000104169-26-000055**; `Revenues` and `OperatingIncomeLoss`, year ended 2026-01-31. |
| Target (TGT) | 2025-02-02 to 2026-01-31 | $104.780 billion | $5.117 billion | **4.88%** = $5.117 billion ÷ $104.780 billion × 100 | 10-K accession **0000027419-26-000016**; `RevenueFromContractWithCustomerExcludingAssessedTax` and `OperatingIncomeLoss`, year ended 2026-01-31. |
| BJ’s Wholesale Club (BJ) | 2025-02-02 to 2026-01-31 | $21.457274 billion | $0.816604 billion | **3.81%** = $0.816604 billion ÷ $21.457274 billion × 100 | 10-K accession **0001531152-26-000007**; `RevenueFromContractWithCustomerExcludingAssessedTax` and `OperatingIncomeLoss`, year ended 2026-01-31. |

Costco’s operating margin sits below Walmart’s and Target’s and slightly above BJ’s on these differing fiscal periods. Its revenue growth, return on average equity and free cash flow provide relevant operating context for the historical earnings multiple, but the assigned evidence does not establish a peer valuation premium or discount: peer P/E multiples are **not established**.

## Future Developments and Strategic Recommendations

1. **Protect member value while measuring sustainable profitability.** As an analyst recommendation, prioritize renewal rates and comparable sales alongside margins rather than maximizing near-term pricing. This follows management’s emphasis on “pricing authority” and its warning that holding prices steady despite cost increases can hurt gross margin (`10-K_0000909832-26-000093.txt:L474-L477`). Cost discipline remains important because “modest changes” in merchandise costs and SG&A can substantially affect net income (`10-K_0000909832-26-000093.txt:L482`).

2. **Expand selectively and evaluate geographic concentration.** Recommend assessing new-location returns and cannibalization before accelerating expansion. The U.S. and Canada accounted for 86% of net sales and 83% of operating income, while new warehouses can draw members from existing locations (“86% and 83%,” `10-K_0000909832-26-000093.txt:L281`; “draw members away,” `10-K_0000909832-26-000093.txt:L284`).

3. **Pair digital investment with resilience and governance.** Recommend evaluating technology projects against service reliability and investment returns. Costco reports “substantial investments in technology and IT projects,” while warning that project failures and inadequately controlled AI systems could harm operations (`10-K_0000909832-26-000093.txt:L300`). The evidence does not establish a quantified financial return from these investments.

4. **Separate tariff-refund benefits from recurring earnings.** Fourth-quarter diluted EPS included a $0.15 non-recurring benefit from refunds net of partial reinvestment (“non-recurring benefit of $0.15 per diluted share,” `EX-99.1_0000909832-26-000084.txt:L25`). Management intends to reinvest most refunds in member value (“invest the majority of the refunds in increased value for the member,” `10-K_0000909832-26-000093.txt:L501`). Accordingly, refund-related earnings should not be extrapolated as a recurring catalyst.

## Investment Recommendation

**Hold.** The thesis-driving figure is Costco’s **43.18× historical P/E**, calculated using the supplied dated share price and reported annual GAAP diluted EPS (Financial Analyst; price source: assigned `price_and_date`; EPS source: `10-K_0000909832-26-000093`, L752). This provides valuation context, but does not establish that the shares are attractively or excessively priced.

Costco’s recurring membership revenue and strong member loyalty support business quality (`10-K_0000909832-26-000093.txt:L481`, L223). However, the supplied evidence establishes neither peer valuation multiples nor forward earnings estimates sufficient to judge whether the historical multiple is justified. Strong operating results alone therefore do not support a Buy, while the multiple alone does not support a Sell. **Hold reflects this valuation-evidence limit, rather than a negative assessment of the business.**
