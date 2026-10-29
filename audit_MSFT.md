# Microsoft substitute report audit

Report: [Microsoft fallback report](runs/MICROSOFT_CORP_2026-10-29_10-27-47-0400/report.md)  
Latest 10-K: `0001193125-26-323660`, year ended 2026-06-30  
Latest 10-Q: `0001193125-26-436133`  
Earnings 8-K and Exhibit 99.1: `0001193125-26-436122`, quarter ended 2026-09-30  
Auditor: AI-assisted, with professor permission; checked 2026-10-29 against the SEC filings and independent arithmetic  
**Errors (Wrong + Unsupported): 0. Missing core claims: 0.**

Sources: [10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm) (`K`; [saved text](runs/MICROSOFT_CORP_2026-10-29_10-27-47-0400/10-K_0001193125-26-323660.txt)), [earnings Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/789019/000119312526436122/msft-ex99_1.htm) (`E`; [saved text](runs/MICROSOFT_CORP_2026-10-29_10-27-47-0400/EX-99.1_0001193125-26-436122.txt)), and [SEC company facts](https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json) (`X`). `E L16` means line 16 of the saved release text. Annual XBRL facts below carry the 10-K accession above. Dollar amounts are billions unless stated otherwise. Correct means equal after rounding to the report's precision.

| # | Claim | Report said | Filing says / independent arithmetic | Mark | Where and definition |
|---|---|---|---|---|---|
| 1 | Total revenue, latest fiscal year | $331.839; prior $281.724 | $331.839 for 2026 and $281.724 for 2025. | Correct | K consolidated income statement; X `RevenueFromContractWithCustomerExcludingAssessedTax`, ends 2026-06-30 and 2025-06-30. Consolidated revenue, not cloud-only revenue. |
| 2 | Revenue growth versus prior year | 17.79% | ($331.839 / $281.724 − 1) × 100 = 17.7887%, or 17.79%. | Correct | K consolidated income statement; same total-revenue definition and 10-K for both years. |
| 3 | Operating income and margin | $155.237; 46.78% | $155.237; $155.237 / $331.839 × 100 = 46.7808%, or 46.78%. | Correct | K consolidated income statement; X `OperatingIncomeLoss`, end 2026-06-30. Denominator is consolidated revenue. |
| 4 | Net income attributable to Microsoft | $133.749 | $133.749. | Correct | K consolidated income statement; X `NetIncomeLoss`, end 2026-06-30. GAAP net income. |
| 5 | GAAP diluted EPS | $17.95 per share | $17.95 per share. | Correct | K consolidated income statement; X `EarningsPerShareDiluted`, end 2026-06-30. Not adjusted EPS. |
| 6 | Return on average equity | 34.04% | $133.749 / (($442.387 + $343.479) / 2) × 100 = 34.0386%, or 34.04%. | Correct | K income statement and balance sheet; X `NetIncomeLoss` and `StockholdersEquity`, ends 2026-06-30 and 2025-06-30. Uses average equity. |
| 7 | Debt to equity | 9.11% | ($31.067 + $9.227) / $442.387 × 100 = 9.1083%, or 9.11%. | Correct | K balance sheet; X `LongTermDebtNoncurrent`, `LongTermDebtCurrent`, `StockholdersEquity`, end 2026-06-30. Includes current portion. |
| 8 | Free cash flow | $66.987 | $182.935 operating cash flow − $115.948 property/equipment additions = $66.987. | Correct | K cash-flow statement; X `NetCashProvidedByUsedInOperatingActivities` and `PaymentsToAcquirePropertyPlantAndEquipment`, end 2026-06-30. |
| 9 | Latest-quarter total revenue | $92.279 | $92.279, versus $77.673 in the comparable prior-year quarter. | Correct | E revenue table, saved lines 213–220; quarter ended 2026-09-30. |
| 10 | Quarter revenue growth | 18.80% | ($92.279 / $77.673 − 1) × 100 = 18.8045%, or 18.80%. | Correct | E revenue table, saved lines 213–220; comparable quarter columns. |
| 11 | Latest-quarter GAAP diluted EPS | $4.92 per share | $4.92 GAAP diluted EPS. The release separately reports $4.89 non-GAAP. | Correct | E L16 and GAAP/non-GAAP reconciliation; quarter ended 2026-09-30. |
| Extra | Azure revenue growth stated outside the financial table | 48% year over year | 48% reported Azure revenue growth. | Correct | E L136. This is Azure growth, not consolidated revenue growth. |
| Extra | Closing share price and date | $531.01 on 2026-10-28 | $531.01 close on 2026-10-28. | Correct | [ChartExchange](https://chartexchange.com/symbol/nasdaq-msft/historical/), [Investing.com](https://www.investing.com/equities/microsoft-corp-historical-data). This external price input is not in SEC filings. |
| Extra | Earnings 8-K acceptance time | 16:04:44 ET after close | 2026-10-28 16:04:44 ET. | Correct | [8-K index](https://www.sec.gov/Archives/edgar/data/789019/000119312526436122/0001193125-26-436122-index.htm), Accepted field. |
| Extra | Historical trailing P/E | 29.58× | $531.01 / $17.95 = 29.5827×, or 29.58×. | Correct | Price source above; K annual GAAP diluted EPS. The close preceded the release; this is not a current quote. |
| Extra | Oracle total revenue | $67.357; FY end 2026-05-31 | $67.357; same FY end. | Correct | [ORCL 10-K](https://www.sec.gov/Archives/edgar/data/1341439/000119312526277521/orcl-20260531.htm), `0001193125-26-277521`; X `Revenues`, end 2026-05-31. |
| Extra | Oracle operating income | $20.606 | $20.606. | Correct | Same ORCL 10-K; X `OperatingIncomeLoss`, end 2026-05-31. |
| Extra | Oracle operating margin | 30.59% | $20.606 / $67.357 × 100 = 30.5922%, or 30.59%. | Correct | Same ORCL 10-K; consolidated operating income / total revenues. |
| Extra | Alphabet total revenue | $402.836; FY end 2025-12-31 | $402.836; same FY end. | Correct | [GOOGL 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm), `0001652044-26-000018`; X `Revenues`, end 2025-12-31. |
| Extra | Alphabet operating income | $129.039 | $129.039. | Correct | Same GOOGL 10-K; X `OperatingIncomeLoss`, end 2025-12-31. |
| Extra | Alphabet operating margin | 32.03% | $129.039 / $402.836 × 100 = 32.0326%, or 32.03%. | Correct | Same GOOGL 10-K; consolidated operating income / total revenues. |
| Template | Five required parts | All five headings present | All five headings present. | Correct | Report headings. |
| Recommendation | Buy, Hold, or Sell cites a correct number | Provisional Hold, citing 29.58× P/E and strong growth | P/E and 17.79% annual revenue growth are marked Correct. | Correct | Report recommendation; Extra P/E and claim 2. This is an investment judgment, not a filing fact. |

Scope: 11 core claims, all additional financial numbers in Valuation Insights (including the inputs within each core claim), the Azure figure stated elsewhere, the five-part template, and the recommendation. No Wrong, Unsupported, or Missing report claim was found. The program's Oracle peer facts omit debt fields despite debt being present under different SEC tags; the report makes no Oracle debt claim, so this is a Lab 02 reader limitation, not a report-audit error. No partner selected or checked this substitute company; that process step is not counted as a missing report claim.
