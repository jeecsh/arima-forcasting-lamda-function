import json
import boto3
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import io
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client('s3')

def handler(event, context):
    try:
        country = event['queryStringParameters']['country']
        
        # S3 bucket and file details
        bucket_name = os.environ.get('BUCKET_NAME')
        file_key = 'co2-data/owid-co2-data.csv'

        
        # Get the file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        csv_content = response['Body'].read().decode('utf-8')
        
        # Read the CSV data into a pandas DataFrame
        df = pd.read_csv(io.StringIO(csv_content))
        
        country_df = df[df['country'] == country][['year', 'co2']].dropna()
        country_df = country_df.set_index('year')
        
        # Fit the ARIMA model
        model = ARIMA(country_df['co2'], order=(5,1,0))
        model_fit = model.fit()
        
        # Forecast the next 10 years
        forecast = model_fit.forecast(steps=10)
        last_year = country_df.index.max()
        forecast_years = [str(year) for year in range(last_year + 1, last_year + 11)]
        forecast_values = forecast.values
        forecast_dict = dict(zip(forecast_years, forecast_values))

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(forecast_dict)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
