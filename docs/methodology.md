# Methodology

## Questions
1. How is each genre associated with anxiety, depression, insomnia and OCD, after accounting for age, listening hours and overlap between genres?
2. Do listeners form distinct taste personas, and do these differ on the four conditions?
3. How much does music information add over an age-and-hours baseline for predicting each condition, and is the signal stable?
4. Which genre-condition hypotheses are worth testing in a controlled medical study?

## Statistical design
- **Association (notebook 01):** Spearman correlation (ordinal exposure), 2,000-sample bootstrap CIs, Benjamini-Hochberg FDR across 64 pairs; then OLS with HC3 robust errors adjusting for age, hours, instrument playing and all 16 genres.
- **Personas (notebook 02):** k-means on standardised genre frequencies; k chosen by silhouette among bootstrap-stable solutions (ARI >= 0.6); persona differences by Kruskal-Wallis (epsilon-squared) and age/hours-adjusted Wald tests.
- **Prediction:** 80/20 stratified split. On the training set, 5x2 repeated CV with identical folds across feature sets. **Pre-specified primary models:** ridge and logistic regression. Random forest and gradient boosting are sensitivity checks with deliberately shallow settings. Feature-set differences are tested with the Nadeau-Bengio corrected resampled t-test and FDR-corrected.
- **Hold-out test:** used once for a pre-listed set of comparisons; no tuning afterwards. 95% bootstrap CIs.
- **Calibration & fairness checks:** out-of-fold calibration curves, Brier skill score vs prevalence, subgroup AUROC (age, listening hours, instrument playing).
- **Importance:** permutation importance on 10 validation folds; a feature is "stable" if positive in >= 80% of folds. SHAP is used for direction only.
- **Evidence synthesis:** a transparent 3-point triage (raw FDR-significant, adjusted p < 0.05 with same sign, stable importance).

## Leakage controls
Imputation, scaling and encoding are inside sklearn pipelines (fit on training folds only). `Music effects` is excluded as a feature. PCA/clustering are unsupervised and used descriptively, not as model inputs.

## Known limitations
Self-reported single-item scores (not validated clinical instruments); cross-sectional, so no causal or temporal claims; self-selected online sample; n = 736 limits power for small effects and rare genres; 153 respondents are minors.
