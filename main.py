from pathlib import Path

import pandas as pd
from fire import Fire
from termcolor import colored

from src.googlemaps import GoogleMapsScraper

SORT_KEYs = {'最相關': 0, '最新': 1, '評分最高': 2, '評分最低': 3}
HEADER = [
    '評論編號', '評論', '評論相對時間', '查詢時間',
    '評分', '使用者名稱', '有幾則評論', '評論者網址',
]


def main(
    urls_file: str,
    num_reviews: int = 2800,
    sort_by: str = '最新',
    output_folder: str = 'output',
    debug: bool = False,
):
    urls = pd.read_csv(urls_file, header=None, index_col=None)
    group_name = Path(urls_file).stem
    output_folder = Path(output_folder, group_name)
    output_folder.mkdir(exist_ok=True, parents=True)
    with GoogleMapsScraper(debug=debug) as scraper:
        for _, (name, url) in urls.iterrows():
            df = pd.DataFrame(columns=HEADER)
            print(colored(f'Scrap {name} {url}...', 'green'))
            error = scraper.sort_by(url, SORT_KEYs[sort_by])
            if error:
                continue

            n = 0
            trial = 0
            while n < num_reviews:

                # logging to std out
                print(colored('[Review ' + str(n) + ']', 'cyan'))

                reviews = scraper.get_reviews(n)
                if len(reviews):
                    for r in reviews:
                        row_data = list(r.values())
                        tmp = pd.DataFrame([row_data], columns=HEADER)
                        df = pd.concat([df, tmp], ignore_index=True)
                        n += 1
                        if n % 30 == 0:
                            df.to_csv(f'{output_folder}/{name}.csv')
                else:
                    trial += 1
                    if trial >= 3 and len(reviews) == 0:
                        break
            df.to_csv(f'{output_folder}/{name}.csv')


if __name__ == '__main__':
    Fire(main)
