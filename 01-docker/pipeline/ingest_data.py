import io
import pandas as pd
import requests
from sqlalchemy import create_engine
from tqdm import tqdm


def run():
  # 1. Configuration parameters
  pg_user = 'root'
  pg_pass = 'root'
  pg_host = 'localhost'
  pg_port = '5432'
  pg_db = 'ny_taxi'

  year = 2021
  month = '01'

  target_table = 'yellow_taxi_data'
  chunksize = 100000

  # 2. Define data types and datetime columns to avoid import warnings
  dtype = {
      'VendorID': 'Int64',
      'passenger_count': 'Int64',
      'trip_distance': 'float64',
      'RatecodeID': 'Int64',
      'store_and_fwd_flag': 'string',
      'PULocationID': 'Int64',
      'DOLocationID': 'Int64',
      'payment_type': 'Int64',
      'fare_amount': 'float64',
      'extra': 'float64',
      'mta_tax': 'float64',
      'tip_amount': 'float64',
      'tolls_amount': 'float64',
      'improvement_surcharge': 'float64',
      'total_amount': 'float64',
      'congestion_surcharge': 'float64',
  }

  parse_dates = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']

  # 3. Setup connection to the PostgreSQL database
  engine = create_engine(
      f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
  )

  # 4. Construct URL dynamically and download the dataset into memory
  prefix = (
      'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow'
  )
  url = f'{prefix}/yellow_tripdata_{year}-{month}.csv.gz'

  print(f'Downloading file for {year}-{month}...')
  response = requests.get(url)
  response.raise_for_status()
  print('File downloaded successfully!')

  # 6. To read the file in chunks
  df_iter = pd.read_csv(
      io.BytesIO(response.content),
      compression='gzip',
      dtype=dtype,
      parse_dates=parse_dates,
      iterator=True,
      chunksize=chunksize,
  )

  # 7. Chunks iteration and ingest data into PostgreSQL
  print('Starting data ingestion into PostgreSQL...')
  first = True
  for df_chunk in tqdm(df_iter):
    if first:
      df_chunk.head(n=0).to_sql(
          name=target_table, con=engine, if_exists='replace'
      )
      first = False

    df_chunk.to_sql(
        name='yellow_taxi_data', con=engine, if_exists='append'
    )

  print('All data successfully loaded!')


if __name__ == '__main__':
  run()