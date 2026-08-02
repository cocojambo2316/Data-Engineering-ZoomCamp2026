import io
import click
import pandas as pd
import requests
from sqlalchemy import create_engine
from tqdm import tqdm


@click.command()
@click.option('--pg_user', default='root', show_default=True)
@click.option('--pg_pass', default='root', show_default=True)
@click.option('--pg_host', default='localhost', show_default=True)
@click.option('--pg_port', default='5432', show_default=True)
@click.option('--pg_db', default='ny_taxi', show_default=True)
@click.option('--year', default=2021, type=int, show_default=True)
@click.option('--month', default='01', type=str, show_default=True)
@click.option('--target_table', default='yellow_taxi_data', show_default=True)
@click.option('--chunksize', default=100000, type=int, show_default=True)
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, target_table, chunksize):
    month = str(month).zfill(2)

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

    engine = create_engine(
        f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    )

    url = (
        'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
        f'yellow_tripdata_{year}-{month}.csv.gz'
    )

    print(f'Downloading file for {year}-{month}...')
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    print('File downloaded successfully!')

    df_iter = pd.read_csv(
        io.BytesIO(response.content),
        compression='gzip',
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )

    print('Starting data ingestion into PostgreSQL...')
    first = True

    for df_chunk in tqdm(df_iter):
        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists='replace' if first else 'append',
            index=False,
        )
        first = False

    print('All data successfully loaded!')


if __name__ == '__main__':
    run()