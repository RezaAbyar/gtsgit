from django.conf import settings
from ..models import Parametrs


class QRValidator:
    def __init__(self, parsed_data):
        self.data = parsed_data
        self.parametr = Parametrs.objects.first()

    def validate_versions(self, gs_instance) -> dict:
        print(self.parametr.rpm_version)
        """Validate all versions and return check results"""
        # First create all individual checks
        checks = {
            'ck_rpm_version': self.data['rpm_version'] in self.parametr.rpm_version,
            'ck_dashboard_version': self.data['dashboard_version'] in self.parametr.dashboard_version,
            'ck_pt_version': self.data['pt_version'] in self.parametr.pt_version,
            'ck_pt_online': self._check_pt_online(gs_instance),
            'ck_quta_table_version': self.data['quta_table_version'] in self.parametr.quta_table_version,
            'ck_price_table_version': self.data['price_zone_versions'][0] in self.parametr.price_table_version,
            'ck_zone_table_version': self._check_zone_table(gs_instance),
            'ck_blacklist_version': True,
            'ck_blacklist_count': self._check_blacklist_count(),
        }
        # Then add the contradiction check based on all other checks
        checks['contradiction'] = not self._check_all_valid(checks)
        return checks

    def _check_pt_online(self, gs_instance) -> bool:
        """Check PT online version"""
        if gs_instance.isonline:
            return self.data['pt_version'] == self.parametr.online_pt_version
        return True

    def _check_zone_table(self, gs_instance) -> bool:
        """Check zone table version"""
        zone_version = self.data['price_zone_versions'][1]
        if not zone_version:
            return True
        if int(gs_instance.zone_table_version) == 0:
            return True
        return int(zone_version) >= int(gs_instance.zone_table_version)

    def _check_blacklist_count(self) -> bool:
        """Check blacklist count"""
        count = int(self.data['blacklist_count'])
        return (
                count <= int(settings.MAX_BLACKLIST_COUNT_ALERT) and
                count >= int(settings.MIN_BLACKLIST_COUNT_ALERT)
        )

    def _check_all_valid(self, checks: dict) -> bool:
        """Check if all validations passed"""
        return all([
            checks['ck_pt_online'],
            checks['ck_blacklist_count'],
            checks['ck_blacklist_version'],
            checks['ck_pt_version'],
            checks['ck_rpm_version'],
            checks['ck_price_table_version'],
            checks['ck_dashboard_version'],
            checks['ck_quta_table_version'],
            checks['ck_zone_table_version']
        ])