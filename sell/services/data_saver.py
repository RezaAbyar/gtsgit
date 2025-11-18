from django.db import transaction
from datetime import datetime, timedelta
import jdatetime
from django.db.models import Count, When, Case

from .validator import QRValidator
from ..models import (
    IpcLog, IpcLogHistory, SellModel,
    Pump, Mojodi, CarInfo, ModemDisconnect, ReceivedBarname
)


class DataSaver:

    def __init__(self, owner_id, parsed_data):

        self.owner_id = owner_id
        self.data = parsed_data
        print(parsed_data)
        self.gs = None
        self.tarikh = None
        self.validator = QRValidator(parsed_data)

    def save_all(self):
        """Save all data from QR code to database"""
        self._get_gs_instance()
        print('saving gs_instance')
        self._prepare_dates()
        print('saving dates')
        self._save_ipc_logs()
        print('saving ipc_logs')
        self._save_modem_disconnects()
        print('saving modem_disconnects')
        self._save_mojodi()
        print('saving mojodi')
        self._save_car_info()
        print('saving car_info')
        self._save_received_barname()
        print('saving received_barname')
        self._save_sell_items()
        print('saving sell_items')
        return self.data

    def _get_gs_instance(self):
        """Get GS instance from database"""
        from base.models import GsModel
        try:
            self.gs = GsModel.objects.get(gsid=self.data['gs_id'])
        except GsModel.DoesNotExist:
            raise DataSavingError(f"GS with id {self.data['gs_id']} not found")

    def _prepare_dates(self):
        """Prepare dates for saving"""
        if self.data['dore'] != "0":
            year = int(self.data['dore'][:4])
            month = int(self.data['dore'][4:6])
            day = int(self.data['dore'][6:8])
            self.tarikh = jdatetime.date(year, month, day).togregorian()
        else:
            self.tarikh = datetime.now().date()

    def _save_ipc_logs(self):
        """Save IPC logs (current and history)"""
        checks = self.validator.validate_versions(self.gs)
        log_data = {
            'gsid': self.data['gs_id'],
            'dore': self.data['dore'],
            'gs': self.gs,
            'date_ipc': self.data['date_ipc'],
            'time_ipc': self.data['time_ipc'],
            'dashboard_version': self.data['dashboard_version'],
            'rpm_version': self.data['rpm_version'],
            'rpm_version_date': self.data['rpm_version_date'],
            'pt_version': self.data['pt_version'],
            'quta_table_version': self.data['quta_table_version'],
            'price_table_version': self.data['price_zone_versions'][0],
            'zone_table_version': self.data['price_zone_versions'][1],
            'blacklist_version': self.data['blacklist_version'],
            'last_connection': self.data['last_connection'],
            'blacklist_count': self.data['blacklist_count'],
            'hd_serial': self.data['hd_serial'],
            'os_version': self.data['os_version'],
            'bl_ipc': self.data['bl_ipc'],
            'modemname': self.data['connector'][0],
            'sam': self.data['connector'][4] == "1",
            'modem': self.data['connector'][1] == "1",
            'poler': self.data['connector'][3] == "1",
            'datacenter': self.data['connector'][2] == "1",
            'fasb': len(self.data['connector']) > 5 and self.data['connector'][5] == "1",
            'asmelat': len(self.data['connector']) > 6 and self.data['connector'][6] == "1",
            'mellatmodem': len(self.data['connector']) > 7 and self.data['connector'][7] == "1",
            'internet': len(self.data['connector']) > 8 and self.data['connector'][8] == "1",
            'updatedate': datetime.now(),
            'uniq': str(self.gs.id),
            'imagever': self.data.get('imagever', '0'),
            'gs_version': self.data.get('gs_version', '0'),
            **checks
        }
        # Update or create IPC log
        IpcLog.objects.update_or_create(
            gs_id=self.gs.id,
            defaults=log_data
        )
        # Create history record
        try:
            log_data['uniq'] = f"{self.gs.id}-{self.data['date_ipc']}"
            IpcLogHistory.objects.create(**log_data)
        except Exception as e:
            pass

    def _save_modem_disconnects(self):
        """Save modem disconnect times if available"""
        try:
            if 'modem_disconnects' in self.data:
                ModemDisconnect.objects.filter(
                    tarikh=self.tarikh,
                    gs_id=self.gs.id
                ).delete()

                disconnects = [
                    ModemDisconnect(
                        gs_id=self.gs.id,
                        tarikh=self.tarikh,
                        starttime=item['ft'],
                        endtime=item['tt'],
                        ip=item['ip']
                    )
                    for item in self.data['modem_disconnects']
                    if item['ft'] != item['tt']
                ]

                if disconnects:
                    ModemDisconnect.objects.bulk_create(disconnects)
                    print(f"Saved {len(disconnects)} modem disconnect records")
                else:
                    print("No valid modem disconnect records to save")

        except Exception as e:
            print(f"Error in _save_modem_disconnects: {str(e)}")
            print(f"Data structure: {self.data.get('modem_disconnects', 'Not found')}")
            # می‌توانید این خطا را لاگ کنید یا به صورت دیگری مدیریت کنید
            # raise DataSavingError(f"Error saving modem disconnects: {str(e)}")

    def _save_received_barname(self):
        """Save received barname data"""
        if 'received_barname' not in self.data or not self.data['received_barname']:
            return

        try:
            # حذف رکوردهای قبلی برای این تاریخ
            ReceivedBarname.objects.filter(
                tarikh=self.tarikh,
                gs_id=self.gs.id
            ).delete()

            barname_list = []
            for item in self.data['received_barname']:
                try:
                    # بررسی وجود کلیدهای ضروری
                    if not all(key in item for key in ['in', 'op', 'q']):
                        print(f"Missing keys in barname item: {item}")
                        continue

                    # تبدیل تاریخ به فرمت مناسب
                    op_date = datetime.strptime(item['op'], '%Y-%m-%d %H:%M:%S').date()

                    barname = ReceivedBarname(
                        gs_id=self.gs.id,
                        tarikh=self.tarikh,
                        barname_number=item['in'],
                        receive_date=op_date,
                        quantity=float(item['q'])
                    )
                    barname_list.append(barname)

                except Exception as e:
                    print(f"Error processing barname item {item}: {str(e)}")
                    continue

            if barname_list:
                ReceivedBarname.objects.bulk_create(barname_list)
                print(f"Saved {len(barname_list)} received barname records")

        except Exception as e:
            print(f"Error in _save_received_barname: {str(e)}")
            print(f"Data structure: {self.data.get('received_barname', 'Not found')}")


    def _save_mojodi(self):
        """Save inventory data"""
        if 'makhzan' not in self.data:
            return

        try:
            # اگر makhzan لیست است، اولین آیتم را بگیرید
            makhzan_data = self.data['makhzan']
            if isinstance(makhzan_data, list):
                makhzan_data = makhzan_data[0] if makhzan_data else {}

            # مقادیر را با مقدار پیش‌فرض 0 بگیرید
            benzin = int(makhzan_data.get('01', 0)) if makhzan_data else 0
            _super = int(makhzan_data.get('02', 0)) if makhzan_data else 0
            gaz = int(makhzan_data.get('03', 0)) if makhzan_data else 0


            pompcount = Pump.objects.filter(gs_id=self.gs.id).aggregate(
                pbenzin=Count(Case(When(product_id=2, then=1))),
                psuper=Count(Case(When(product_id=3, then=1))),
                pgaz=Count(Case(When(product_id=4, then=1))),
            )

            if pompcount['pbenzin'] == 0:
                benzin = 0
            if pompcount['psuper'] == 0:
                _super = 0
            if pompcount['pgaz'] == 0:
                gaz = 0

            yesterday = self.tarikh - timedelta(days=1)
            uniq = f'{self.gs.id}-{self.tarikh}'
            Mojodi.objects.filter(uniq=uniq).delete()
            Mojodi.objects.update_or_create(
                gs_id=self.gs.id,
                tarikh=self.tarikh,
                defaults={
                    'benzin': benzin,
                    'super': _super,
                    'gaz': gaz,
                    'uniq':uniq
                }
            )
        except Exception as e:
            print(f"Error in _save_mojodi: {str(e)}")
            raise

    def _save_car_info(self):
        """Save car information if available"""
        if 'car_info' in self.data and self.data['dashboard_version'] != '1.02.101701':
            CarInfo.objects.filter(gs__gsid=self.data['gs_id'], tarikh=self.tarikh).delete()

            for i, value in enumerate(self.data['car_info']):
                if float(value) > 0:
                    CarInfo.objects.create(
                        gs_id=self.gs.id,
                        tarikh=self.tarikh,
                        carstatus_id=i + 1,
                        amount=value
                    )

    def _save_sell_items(self):
        """Save sell items data"""
        for item in self.data['sell_items']:
            product_map = {
                '01': 2,  # بنزین
                '02': 3,  # سوپر
                '03': 4,  # گاز
                '04': 948  # نفت
            }

            product_id = product_map.get(item['product_code'], 0)
            if product_id == 0:
                continue

            # Convert amounts to Rials
            amounts = {
                'yarane': int(item['yarane1']) / 100 if int(item['yarane1']) > 0 else 0,
                'azad': int(item['azad']) / 100 if int(item['azad']) > 0 else 0,
                'ezterari': int(item['ezterari']) / 100 if int(item['ezterari']) > 0 else 0,
                'haveleh': int(item['haveleh']) / 100 if int(item['haveleh']) > 0 else 0,
                'azmayesh': int(item['azmayesh']) / 100 if int(item['azmayesh']) > 0 else 0
            }

            # Special cases for yarane
            if product_id == 2:  # بنزین
                amounts['yarane'] = int(item['yarane1']) / 100 if int(item['yarane1']) > 0 else 0
            elif product_id == 4:  # گاز
                amounts['yarane'] = int(item['yarane2']) / 100 if int(item['yarane2']) > 0 else 0

            # Get or create pump
            pump, _ = Pump.objects.get_or_create(
                number=int(item['pump_number']),
                gs_id=self.gs.id,
                defaults={'product_id': product_id}
            )

            if pump.product_id != product_id:
                pump.product_id = product_id
                pump.save()

            # Calculate total sell
            total_sell = sum(amounts.values())

            # Create or update sell record
            SellModel.objects.update_or_create(
                uniq=f"{self.tarikh}-{self.gs.id}-{pump.id}",
                defaults={
                    'gs_id': self.gs.id,
                    'tolombeinfo_id': pump.id,
                    'product_id': product_id,
                    'pumpnumber': pump.number,
                    'tarikh': self.tarikh,
                    'dore': self.data['dore'],
                    'mindatecheck': item['mindatecheck'],
                    **amounts,
                    'sellkol': total_sell
                }
            )


class DataSavingError(Exception):
    pass
