# Costco report audit

Report: [Costco fallback report](runs/COSTCO_WHOLESALE_CORP_NEW_2026-10-29_10-25-40-0400/report.md)  
Latest 10-K: `0000909832-26-000093`, year ended 2026-08-30  
Latest 10-Q: `0000909832-26-000051`  
Earnings 8-K and Exhibit 99.1: `0000909832-26-000084`, 16-week quarter ended 2026-08-30  
Auditor: AI-assisted, with professor permission; checked 2026-10-29 against the SEC filings and independent arithmetic  
**Errors (Wrong + Unsupported): 0. Missing core claims: 0.**

Sources: [10-K](https://www.sec.gov/Archives/edgar/data/909832/000090983226000093/cost-20260830.htm) (`K`; [saved text](runs/COSTCO_WHOLESALE_CORP_NEW_2026-10-29_10-25-40-0400/10-K_0000909832-26-000093.txt)), [Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/909832/000090983226000084/costex9918-k92426.htm) (`E`; [saved text](runs/COSTCO_WHOLESALE_CORP_NEW_2026-10-29_10-25-40-0400/EX-99.1_0000909832-26-000084.txt)), and [SEC company facts](https://data.sec.gov/api/xbrl/companyfacts/CIK0000909832.json) (`X`). `K L735` means saved 10-K line 735. Annual XBRL facts below carry the 10-K accession above. Dollar amounts are billions unless stated otherwise. Correct means equal after rounding to the report's precision.

| # | Claim | Report said | Filing says / independent arithmetic | Mark | Where and definition |
|---|---|---|---|---|---|
| 1 | Total revenue, latest fiscal year | $303.154; prior $275.235 | 2026: $297.247 net sales + $5.907 membership fees = $303.154. 2025: $269.912 + $5.323 = $275.235. | Correct | K L733–735; X `RevenueFromContractWithCustomerExcludingAssessedTax`, ends 2026-08-30 and 2025-08-31. The tag holds total revenue here. |
| 2 | Revenue growth versus prior year | 10.14% | ($303.154 / $275.235 − 1) × 100 = 10.1437%, or 10.14%. | Correct | K L735; same total-revenue definition and 10-K for both years. |
| 3 | Operating income and margin | $11.685; 3.85% | $11.685; $11.685 / $303.154 × 100 = 3.8545%, or 3.85%. | Correct | K L735, L739; X `OperatingIncomeLoss`, end 2026-08-30. Denominator is total revenue. |
| 4 | Net income attributable to Costco | $9.226 | $9.226. | Correct | K L747; X `NetIncomeLoss`, end 2026-08-30. |
| 5 | GAAP diluted EPS | $20.76 per share | $20.76 per share. | Correct | K L752; X `EarningsPerShareDiluted`, end 2026-08-30. |
| 6 | Return on average equity | 28.40% | $9.226 / (($35.803 + $29.164) / 2) × 100 = 28.4021%, or 28.40%. | Correct | K L747, L829; X `NetIncomeLoss` and `StockholdersEquity`, ends 2026-08-30 and 2025-08-31. Uses average equity. |
| 7 | Debt to equity | 17.21% | ($3.914 + $2.248) / $35.803 × 100 = 17.2108%, or 17.21%. | Correct | K L808, L812, L829; X `LongTermDebtNoncurrent`, `LongTermDebtCurrent`, `StockholdersEquity`, end 2026-08-30. Includes current portion. |
| 8 | Free cash flow | $9.382 | $15.817 operating cash flow − $6.435 property/equipment additions = $9.382. | Correct | K L893, L895; X `NetCashProvidedByUsedInOperatingActivities` and `PaymentsToAcquirePropertyPlantAndEquipment`, end 2026-08-30. |
| 9 | Latest-quarter total revenue | $95.723 | $95.723, versus $86.156 in the comparable prior-year quarter. | Correct | E L53; total revenue, not net sales; 16 weeks ended 2026-08-30. |
| 10 | Quarter revenue growth | 11.10% | ($95.723 / $86.156 − 1) × 100 = 11.1043%, or 11.10%. | Correct | E L53; the two comparable 16-week columns. |
| 11 | Latest-quarter GAAP diluted EPS | $6.75 per share | $6.75 diluted EPS. | Correct | E L25 and the release per-share table. |
| Extra | Closing share price and date | $896.48 on 2026-09-24 | $896.48 close on 2026-09-24. | Correct | [Stock Analysis](https://stockanalysis.com/stocks/cost/history/), [ChartExchange](https://chartexchange.com/symbol/nasdaq-cost/historical/). This external price input is not in SEC filings. |
| Extra | Earnings 8-K acceptance time | 16:17:37 ET after close | 2026-09-24 16:17:37 ET. | Correct | [8-K index](https://www.sec.gov/Archives/edgar/data/909832/000090983226000084/0000909832-26-000084-index.htm), Accepted field. |
| Extra | Historical trailing P/E | 43.18× | $896.48 / $20.76 = 43.1830×, or 43.18×. | Correct | Price source above; K L752 annual GAAP EPS. The close preceded the release; EPS was disclosed later. Not a current quote. |
| Extra | Walmart total revenue | $713.163; FY end 2026-01-31 | $713.163; same FY end. | Correct | [WMT 10-K](https://www.sec.gov/Archives/edgar/data/104169/000010416926000055/wmt-20260131.htm), `0000104169-26-000055`; X `Revenues`, end 2026-01-31; total revenues. |
| Extra | Walmart operating income | $29.825 | $29.825. | Correct | Same WMT 10-K; X `OperatingIncomeLoss`, end 2026-01-31. |
| Extra | Walmart operating margin | 4.18% | $29.825 / $713.163 × 100 = 4.1821%, or 4.18%. | Correct | Same WMT 10-K; consolidated operating income / total revenues. |
| Extra | Target consolidated revenue | $104.780; FY end 2026-01-31 | $104.780; same FY end. Statement label: **Net sales**. | Correct | [TGT 10-K](https://www.sec.gov/Archives/edgar/data/27419/000002741926000016/tgt-20260131.htm), `0000027419-26-000016`; X `RevenueFromContractWithCustomerExcludingAssessedTax`, end 2026-01-31. This is its consolidated top line, not one component below a separate total. |
| Extra | Target operating income | $5.117 | $5.117. | Correct | Same TGT 10-K; X `OperatingIncomeLoss`, end 2026-01-31. |
| Extra | Target operating margin | 4.88% | $5.117 / $104.780 × 100 = 4.8836%, or 4.88%. | Correct | Same TGT 10-K; operating income / consolidated top line. |
| Extra | BJ's total revenue | $21.457274; FY end 2026-01-31 | $20.957502 net sales + $0.499772 membership fees = $21.457274. | Correct | [BJ 10-K](https://www.sec.gov/Archives/edgar/data/1531152/000153115226000007/bj-20260131.htm), `0001531152-26-000007`; X `RevenueFromContractWithCustomerExcludingAssessedTax`, end 2026-01-31; total revenue. |
| Extra | BJ's operating income | $0.816604 | $0.816604. | Correct | Same BJ 10-K; X `OperatingIncomeLoss`, end 2026-01-31. |
| Extra | BJ's operating margin | 3.81% | $0.816604 / $21.457274 × 100 = 3.8057%, or 3.81%. | Correct | Same BJ 10-K; operating income / total revenue. |
| Template | Five required parts | All five headings present | All five headings present. | Correct | Report headings. |
| Recommendation | Buy, Hold, or Sell cites a correct number | Provisional Hold, citing 43.18× P/E and revenue growth | P/E and 10.14% growth are marked Correct. | Correct | Report recommendation; Extra P/E and claim 2. This is an investment judgment, not a filing fact. |

Scope: 11 core claims, all additional financial numbers in Valuation Insights (including the inputs within each core claim), the five-part template, and the recommendation. No Wrong, Unsupported, or Missing report claim was found. The professor's undisclosed Tuesday price was not verified; the report discloses and uses a sourced substitute close.
