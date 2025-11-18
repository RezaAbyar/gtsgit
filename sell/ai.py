import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from sell.models import SellGs, SellModel


# دریافت داده‌های فروش از مدل SellGs
def get_sales_data(gs_id):

    sales = SellModel.objects.filter(gs_id=gs_id,product_id=2).values('create', 'sellkol')
    df = pd.DataFrame(list(sales))
    df['create'] = pd.to_datetime(df['create'])
    df.set_index('create', inplace=True)
    return df


# آماده‌سازی داده‌ها
def prepare_data(df):
    df['day'] = df.index.day
    df['month'] = df.index.month
    df['year'] = df.index.year
    return df[['day', 'month', 'year', 'sellkol']]


# پیش‌بینی فروش با استفاده از رگرسیون خطی
def predict_sales(gs_id, num_days=10):
    df = get_sales_data(gs_id)
    data = prepare_data(df)

    X = data[['day', 'month', 'year']]
    y = data['sellkol']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    model = LinearRegression()
    model.fit(X_train, y_train)

    future_dates = pd.date_range(df.index[-1] + pd.Timedelta(days=1), periods=num_days, freq='D')
    future_data = pd.DataFrame({
        'day': future_dates.day,
        'month': future_dates.month,
        'year': future_dates.year
    })

    future_sales = model.predict(future_data)

    return future_dates, future_sales


# نمونه استفاده از تابع
gs_id = 777  # شناسه جایگاه
future_dates, future_sales = predict_sales(gs_id)

for date, sales in zip(future_dates, future_sales):
    print(f"date: {date},  Sell: {sales}")


import os
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

# مسیر فایل لاگ


# نام فایل لاگ
LOG_FILE = r'e:/django.txt'

# تنظیمات لاگ‌گیری
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_FILE,
            'when': 'midnight',  # هر روز در نیمه‌شب چرخش انجام شود
            'backupCount': 7,  # تعداد فایل‌های قدیمی که نگهداری می‌شوند
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
