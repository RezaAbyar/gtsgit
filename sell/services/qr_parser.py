import json
import re
from datetime import datetime
from typing import Dict, List, Tuple


class QRParser:
    @staticmethod
    def parse_qr_data(data: str) -> Dict:
        """Parse QR code data into structured dictionary"""
        try:

            # Clean and split data
            data = data.replace('@@@@@@@@@@', '').replace("b'", "").replace("'", "")
            sections = data.split("#")
            print(data)
            # Parse main information
            info = sections[0].split(",")

            parsed = {
                'gs_id': info[0][-4:],
                'dore': info[1],
                'date_ipc': info[2],
                'time_ipc': info[3],
                'dashboard_version': info[4],
                'rpm_version': info[5],
                'rpm_version_date': info[6],
                'pt_version': info[7],
                'quta_table_version': info[8],
                'price_zone_versions': info[9].split("-"),
                'blacklist_version': info[10],
                'last_connection': info[11],
                'blacklist_count': info[12],
                'hd_serial': info[13],
                'os_version': info[14],
                'bl_ipc': info[15],
                'connector': info[16],
                'ismotabar': info[17][:1],
                'imagever': info[18] if len(info) > 18 else '0',
                'gs_version': info[19][:5] if len(info) > 19 else '0'
            }

            # Parse modem disconnects if available
            if parsed['dashboard_version'] in ['1.04.020701', '1.04.021501', '1.04.050701']:
                json_sections = re.findall(r'(\[\{.*?\}\])', data)
                print(f"Found {len(json_sections)} JSON-like sections: {json_sections}")

                for section in json_sections:
                    try:
                        # تمیز کردن و تبدیل به JSON
                        cleaned = section.replace("'", '"')
                        json_data = json.loads(cleaned)

                        # تشخیص نوع داده بر اساس ساختار
                        if isinstance(json_data, list) and json_data:
                            first_item = json_data[0]

                            if 'ft' in first_item and 'tt' in first_item and 'ip' in first_item:
                                # این بخش قطعی مودم است
                                parsed['modem_disconnects'] = json_data
                                print("Found modem disconnects:", json_data)

                            elif 'in' in first_item and 'op' in first_item and 'q' in first_item:
                                # این بخش بارنامه است
                                parsed['received_barname'] = json_data
                                print("Found barname data:", json_data)

                            else:
                                print("Unknown JSON structure:", json_data)

                    except json.JSONDecodeError as e:
                        print(f"Error parsing section {section}: {str(e)}")
                        continue

            # Parse makhzan data
            makhzan_part = re.search(r'\[(\{.*?\})\]', data)

            if makhzan_part:
                try:
                    # تمیز کردن داده‌ها و تبدیل به فرمت JSON معتبر
                    cleaned = makhzan_part.group(1).replace("'", '"')
                    parsed['makhzan'] = json.loads(f'[{cleaned}]')
                except json.JSONDecodeError as e:
                    print(f"Error parsing makhzan data: {str(e)}")
                    parsed['makhzan'] = []

            # Parse car info if available
            car_section = re.search(r'\[(\d+\.\d+,\d+\.\d+.*?)\]', data)
            if car_section:
                parsed['car_info'] = car_section.group(1).split(",")



            # Parse sell items
            parsed['sell_items'] = []
            for item in sections[1:]:
                sell_data = item.split(",")
                if len(sell_data) >= 8:
                    parsed['sell_items'].append({
                        'pump_number': sell_data[0],
                        'product_code': sell_data[1],
                        'yarane1': sell_data[2],
                        'yarane2': sell_data[3],
                        'azad': sell_data[4],
                        'ezterari': sell_data[5],
                        'azmayesh': sell_data[6],
                        'haveleh': sell_data[7].replace("'", ""),
                        'mindatecheck': sell_data[8].replace("'", "") if len(sell_data) > 8 else "0"
                    })

            return parsed

        except Exception as e:
            print(f"Error parsing QR data: {str(e)}")
            raise QRParsingError(f"Error parsing QR data: {str(e)}")


class QRParsingError(Exception):
    pass
