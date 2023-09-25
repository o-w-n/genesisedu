import csv
import json
import requests


def save_json(json_data, filename):
    try:
        with open(filename, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
    except Exception as ex:
        print(str(ex))


def save_csv(data_dict, csv_filename):
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Year',
                'App ID',
                'Top Free Number',
                'Top Free Different',
                'Top Free Name',
                'Top Free Publisher',
                'Top Free Tags',
                'Top Free Downloads',
                'Top Grossing Number',
                'Top Grossing Different',
                'Top Grossing Name',
                'Top Grossing Publisher',
                'Top Grossing Tags',
                'Top Grossing Revenue'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for year, app_data in data_dict.items():
                for app_id, app_info in app_data.items():
                    top_free_info = app_info['top_free']
                    top_grossing_info = app_info['top_grossing']
                    writer.writerow({
                        'Year': year,
                        'App ID': app_id,
                        'Top Free Number': top_free_info['number'],
                        'Top Free Different': top_free_info['different'],
                        'Top Free Name': top_free_info['name'],
                        'Top Free Publisher': top_free_info['publisher'],
                        # 'Top Free Tags': ', '.join(top_free_info['tags']),
                        'Top Free Downloads': top_free_info.get('downloads', ''),
                        'Top Grossing Number': top_grossing_info['number'],
                        'Top Grossing Different': top_grossing_info['different'],
                        'Top Grossing Name': top_grossing_info['name'],
                        'Top Grossing Publisher': top_grossing_info['publisher'],
                        # 'Top Grossing Tags': ', '.join(top_grossing_info['tags']),
                        'Top Grossing Revenue': top_grossing_info.get('revenue', '')
                    })
        print(f'Data saved to {csv_filename}')
    except Exception as ex:
        print(str(ex))


def get_data(api_url, params=None, headers=None):
    try:
        response = requests.get(api_url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"error: {response.status_code}")
            return None
    except Exception as ex:
        print(str(ex))
        return None


def process_app_data(app_data, is_top_free=True):
    tags_list = []

    for tags_data in app_data['top_free']['application']['tags']:
        if tags_data['type'] == 'apps':
            tags_list.append(tags_data['name'].replace(': Other', ''))

    app_dict = {
        'number': app_data['top_free' if is_top_free else 'top_grossing'][
            'top_free' if is_top_free else 'top_grossing'],
        'different': app_data['top_free' if is_top_free else 'top_grossing']['diff'],
        'name': app_data['top_free' if is_top_free else 'top_grossing']['application']['name'],
        'publisher': app_data['top_free' if is_top_free else 'top_grossing']['application']['publisher']['name'],
        # 'tags': tags_list
    }

    if is_top_free:
        app_dict['downloads'] = app_data['top_free']['downloads']
    else:
        app_dict['revenue'] = app_data['top_grossing']['revenue']

    return app_dict


def main():
    url = "https://appmagic.rocks/api/v1/top"
    base_params = {
        "aggregation": "year",
        "topDepth": "1000",
        "store": "5",
        "country": "WW",
        "kind": "all",
        "tag": "31"
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Bearer 8j3mR92pa9WtdCTO9lHzISrmwVXzzwPf",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }

    result_data = {}

    for year in range(2015, 2023 + 1):
        params = {
            **base_params,
            "date": f"{year}-01-01"
        }
        response_data = get_data(url, params=params, headers=headers)
        if response_data:
            app_dict = {}

            for app_data in response_data['data']:
                try:
                    app_id = app_data['top_grossing']['application']['united_application_id']
                    if app_id is not None:
                        top_free_data = process_app_data(app_data, is_top_free=True)
                        top_grossing_data = process_app_data(app_data, is_top_free=False)

                        app_dict[app_id] = {
                            'top_free': top_free_data,
                            'top_grossing': top_grossing_data
                        }
                except:
                    pass

            result_data[str(year)] = app_dict
    return result_data


if __name__ == '__main__':
    data = main()
    save_csv(data, 'app_data.csv')
    save_json(data, 'app_data.json')
