"""Fifteen reproducible, training-only views for each assessed notebook."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

FLIGHT_CHARTS = ['Price distribution', 'Cabin frequency', 'Origin frequency', 'Destination frequency', 'Agency frequency',
                 'Flight duration distribution', 'Distance distribution', 'Monthly booking volume', 'Price by cabin',
                 'Price by agency', 'Distance versus price', 'Duration versus price', 'Median route prices',
                 'Numeric correlations', 'Monthly median prices']
CLASS_CHARTS = ['Source label balance', 'Age distribution', 'Company representation', 'Age by label', 'Label mix by company',
                'Age by company', 'Label mix by age band', 'Mean age by company', 'Median age by label',
                'Age distributions by label', 'Company and label counts', 'Age spread by company',
                'Youngest age band by company', 'Oldest age band by company', 'Company representation within labels']
HOTEL_CHARTS = ['Historical hotel popularity', 'Destination booking volume', 'Stay duration distribution', 'Nightly price distribution',
                'Total spend distribution', 'Monthly booking volume', 'Nightly price by hotel', 'Stay length by hotel',
                'Stay length versus total', 'Nightly price versus total', 'Bookings per user', 'Distinct hotels per user',
                'Repeat booking fraction by hotel', 'Monthly average stay', 'Hotel and destination mapping']


def draw_chart(task, index, frame):
    """Return the chart and a measured observation, without causal claims."""
    df = frame.copy()
    fig, ax = plt.subplots(figsize=(9, 4.4))
    sns.set_theme(style='whitegrid', palette='deep')
    titles = {'flights': FLIGHT_CHARTS, 'classification': CLASS_CHARTS, 'hotels': HOTEL_CHARTS}[task]
    insight = ''
    def counts(column):
        nonlocal insight
        values = df[column].value_counts().sort_values()
        values.plot.barh(ax=ax)
        insight = f'{values.index[-1]} has the largest count ({int(values.iloc[-1]):,}) in the training partition.'
    def histogram(column):
        nonlocal insight
        ax.hist(df[column], bins=30, color='#207e89')
        ax.set_xlabel(column)
        insight = f'{column}: median={df[column].median():.2f}; 10th–90th percentile={df[column].quantile(.1):.2f}–{df[column].quantile(.9):.2f}.'
    def boxes(category, numeric):
        nonlocal insight
        sns.boxplot(data=df, x=category, y=numeric, ax=ax, showfliers=False)
        medians = df.groupby(category)[numeric].median()
        insight = f'Median {numeric} ranges from {medians.min():.2f} to {medians.max():.2f} across {category} groups. Differences do not establish causation.'
    def scatter(x, y):
        nonlocal insight
        sample = df.sample(min(1500, len(df)), random_state=42)
        ax.scatter(sample[x], sample[y], s=8, alpha=.25, color='#207e89')
        ax.set(xlabel=x, ylabel=y)
        insight = f'Training Pearson correlation between {x} and {y}: {df[x].corr(df[y]):.3f}. Plot capped at 1,500 sampled records for readability.'
    if task == 'flights':
        if index == 0: histogram('price')
        elif 1 <= index <= 4: counts(['flightType', 'from', 'to', 'agency'][index-1])
        elif index in [5, 6]: histogram('time' if index == 5 else 'distance')
        elif index in [7, 14]:
            values = df.set_index('date').resample('MS').price.agg('count' if index == 7 else 'median')
            values.plot(ax=ax); insight = f'Monthly values range from {values.min():.2f} to {values.max():.2f}. Partial boundary months can affect the comparison.'
        elif index in [8, 9]: boxes('flightType' if index == 8 else 'agency', 'price')
        elif index in [10, 11]: scatter('distance' if index == 10 else 'time', 'price')
        elif index == 12:
            table = df.pivot_table(index='from', columns='to', values='price', aggfunc='median')
            sns.heatmap(table, ax=ax, cmap='Blues'); insight = f'{int(table.notna().sum().sum())} origin/destination cells contain historical observations; blank cells are not zero fares.'
        else:
            sns.heatmap(df[['price', 'time', 'distance']].corr(), annot=True, ax=ax, cmap='coolwarm', vmin=-1, vmax=1)
            insight = 'Correlated duration and distance can provide overlapping information; associations do not establish future pricing accuracy.'
    elif task == 'classification':
        df['age_band'] = pd.cut(df.age, bins=[17, 29, 39, 49, 59, 101])
        if index == 0: counts('gender')
        elif index == 1: histogram('age')
        elif index == 2: counts('company')
        elif index == 3: boxes('gender', 'age')
        elif index in [4, 6, 14]:
            category = 'age_band' if index == 6 else 'company'
            table = pd.crosstab(df[category], df.gender, normalize='columns' if index == 14 else 'index')
            table.plot.bar(stacked=True, ax=ax)
            insight = 'Group proportions show representation in the training sample; they are not evidence of a reliable identity classifier.'
        elif index == 5: boxes('company', 'age')
        elif index in [7, 8, 11]:
            group = 'gender' if index == 8 else 'company'
            statistic = 'median' if index == 8 else ('std' if index == 11 else 'mean')
            values = df.groupby(group).age.agg(statistic)
            values.plot.bar(ax=ax)
            insight = f'{statistic.title()} age ranges from {values.min():.2f} to {values.max():.2f}; group sample sizes must also be considered.'
        elif index == 9:
            for label, sub in df.groupby('gender'): ax.hist(sub.age, bins=12, alpha=.4, label=label)
            ax.legend(); insight = 'Overlapping age distributions limit the usefulness of a single age-based rule; confirm this with held-out metrics.'
        elif index == 10:
            sns.heatmap(pd.crosstab(df.company, df.gender), annot=True, fmt='d', ax=ax, cmap='Blues')
            insight = 'Counts identify small company/label subgroups where aggregate accuracy could conceal poor performance.'
        else:
            flag = df.age < 30 if index == 12 else df.age >= 60
            values = df.assign(flag=flag).groupby('company').flag.mean()
            values.plot.bar(ax=ax)
            insight = f'The selected age-band share ranges from {values.min():.1%} to {values.max():.1%}; company composition may act as a proxy and requires cautious interpretation.'
    else:
        if index in [0, 1]: counts('name' if index == 0 else 'place')
        elif index in [2, 3, 4]: histogram(['days', 'price', 'total'][index-2])
        elif index in [5, 13]:
            values = df.set_index('date').resample('MS').days.agg('count' if index == 5 else 'mean')
            values.plot(ax=ax); insight = f'Monthly values range from {values.min():.2f} to {values.max():.2f}; this is historical booking behavior.'
        elif index in [6, 7]: boxes('name', 'price' if index == 6 else 'days')
        elif index in [8, 9]: scatter('days' if index == 8 else 'price', 'total')
        elif index in [10, 11]:
            values = df.groupby('userCode')['name'].agg('size' if index == 10 else 'nunique')
            ax.hist(values, bins=20); insight = f'Per-user median is {values.median():.1f}; this determines how much history personalization can use.'
        elif index == 12:
            ordered = df.sort_values('date')
            repeated = ordered.duplicated(['userCode', 'name'])
            values = ordered.assign(repeat=repeated).groupby('name')['repeat'].mean()
            values.plot.bar(ax=ax); insight = f'Repeat booking share ranges from {values.min():.1%} to {values.max():.1%}; repeat hotels should remain eligible recommendations.'
        else:
            table = pd.crosstab(df['name'], df.place).gt(0).astype(int)
            sns.heatmap(table, ax=ax, cmap='Blues', cbar=False)
            insight = f'There are {int(table.sum().sum())} observed hotel/destination pairs. A fixed destination may leave no ranking choice.'
    ax.set_title(titles[index], loc='left', pad=15)
    if len(ax.get_xticklabels()) > 0: plt.setp(ax.get_xticklabels(), rotation=40, ha='right')
    fig.tight_layout()
    return fig, insight
