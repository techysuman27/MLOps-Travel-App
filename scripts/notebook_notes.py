"""Chart-specific reasoning; observed numerical results remain in executed outputs."""
CHART_NOTES = {
 'flights': [
  ('Inspect the target distribution before selecting error measures.', 'Use MAE for interpretable budget error and RMSE to expose costly large mistakes; retain valid high fares.'),
  ('Count cabin categories to check training support.', 'Evaluate errors by cabin so the most common class does not hide weak performance in a smaller class.'),
  ('Compare origin coverage.', 'Limit predictions to supported origins and collect more observations where training coverage is thin.'),
  ('Compare destination coverage independently of origins.', 'A supported destination does not guarantee every route has enough observations; inspect route combinations too.'),
  ('Count the records supplied by each agency.', 'An agency-level error comparison needs sample sizes, because an overall average can be dominated by a larger agency.'),
  ('Inspect flight duration and its observed range.', 'Validate duration at serving time and flag implausible inputs; historical duration support is not a live schedule.'),
  ('Inspect distance variation and extreme values.', 'Retain supported long routes while recognizing that distance units are not established by the course schema.'),
  ('Plot booking counts through time to assess temporal coverage.', 'Use a chronological holdout; partial months and uneven coverage can distort apparent demand changes.'),
  ('Compare fare distributions across cabin classes.', 'Cabin is a plausible pricing feature, but its predictive contribution must survive held-out evaluation.'),
  ('Compare agency fare distributions.', 'Agency differences may reflect route and cabin mix, so this chart alone cannot justify a causal pricing claim.'),
  ('Inspect the association between distance and fare.', 'A curved or dispersed relationship motivates nonlinear candidates; distance alone cannot account for all pricing variation.'),
  ('Inspect duration versus fare.', 'Duration may overlap with distance. Check permutation importance and error slices before claiming an independent effect.'),
  ('Display route-level median fares and missing combinations.', 'Blank cells indicate absent evidence, not free flights; route-specific coverage affects the reliability of estimates.'),
  ('Compare correlations among fare, duration and distance.', 'Correlated inputs can make individual importance values misleading; the complete pipeline must be evaluated together.'),
  ('Track monthly median fares alongside the earlier volume chart.', 'Apparent trends may reflect route/cabin mix. Do not extrapolate current fares from this historical series.')
 ],
 'classification': [
  ('Check the support for every source label, including none.', 'Keep all documented source categories in evaluation; none has no established identity meaning.'),
  ('Inspect age coverage and spread.', 'Avoid extrapolating beyond the observed age range; age is a limited feature for this educational benchmark.'),
  ('Measure company representation.', 'A heavily represented company could dominate aggregate metrics; inspect company-level counts before interpreting performance.'),
  ('Compare age distributions across source labels.', 'Strong overlap would limit simple age-based separation; confirm any apparent differences using held-out macro F1.'),
  ('Compare within-company label proportions.', 'Company may be a dataset-specific proxy. These proportions do not justify decisions about an individual.'),
  ('Compare age distributions across companies.', 'Age and company composition may be related; avoid interpreting either as an independent cause of a label.'),
  ('Compare label proportions across age bands.', 'Binning can reveal coverage gaps but also hide within-band variation; use original age in the fitted pipeline.'),
  ('Compare average ages across companies.', 'Mean differences describe sample composition and do not establish predictive usefulness.'),
  ('Compare median ages across labels.', 'Similar medians support checking a weak-signal baseline instead of assuming that classification must work well.'),
  ('Overlay age distributions for the source labels.', 'Overlapping distributions explain why an age threshold may fail; retain uncertainty and baseline comparisons.'),
  ('Inspect company-by-label sample sizes.', 'Small cells make per-group estimates unstable; aggregate accuracy should not conceal sparse subgroup evidence.'),
  ('Compare age standard deviations across companies.', 'Different age spreads affect feature coverage, even when company means look similar.'),
  ('Measure the share of users younger than 30 in each company.', 'This describes company composition only; the threshold is exploratory and is not a classification rule.'),
  ('Measure the share of users aged 60 or above in each company.', 'Sparse older age groups limit conclusions about generalization for those users.'),
  ('Reverse the normalization to show company representation within each label.', 'The denominator changes the question: company composition within a label differs from label probability within a company.')
 ],
 'hotels': [
  ('Count historical bookings for each hotel.', 'Popularity provides a transparent cold-start baseline that personalized ranking must improve upon.'),
  ('Compare booking volumes across destinations.', 'In this catalogue each destination has one hotel; destination popularity and hotel popularity are tightly linked.'),
  ('Inspect the distribution of stay lengths.', 'Stay duration supports budget estimates and preference analysis, but does not represent availability.'),
  ('Inspect recorded nightly prices.', 'A budget filter should use the recorded nightly price and clearly state that current market rates are unavailable.'),
  ('Inspect total booking spend.', 'Total combines nightly price and duration; it should not be mistaken for an independent measure of hotel quality.'),
  ('Plot historical booking volume over time.', 'Use later bookings for evaluation, and avoid interpreting a partial boundary month as a demand shock.'),
  ('Compare nightly prices across hotels.', 'Price differences support budget filtering; they do not establish service quality or a causal preference.'),
  ('Compare stay lengths across hotels.', 'Historical stay patterns can guide future preference features, but the present ranker uses booking interactions.'),
  ('Inspect the relationship between stay duration and total cost.', 'The arithmetic relationship is expected; it is not evidence that longer stays cause higher nightly prices.'),
  ('Inspect nightly price versus total cost.', 'Duration also drives total cost. Show nightly and total estimates separately when discussing affordability.'),
  ('Count each user\'s historical bookings.', 'Users with little history need a popularity fallback; repeated interactions offer stronger preference evidence.'),
  ('Count distinct hotels visited by each user.', 'A small personal catalogue limits collaborative evidence and motivates reporting recommendation coverage.'),
  ('Measure repeated user-hotel bookings in chronological order.', 'Keep previously visited hotels eligible: repeat bookings are valid targets in this travel use case.'),
  ('Track average stay length by month.', 'Changing duration can affect total budgets without changing hotel preference; monitor it separately from ranking accuracy.'),
  ('Map hotels to destinations explicitly.', 'One hotel per city means a destination-filtered result is a lookup; richer within-city choices require more data.')
 ]
}
