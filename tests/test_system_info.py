from unittest.mock import patch, MagicMock
from app.utils.system_info import SystemInfo


class TestSystemInfoHelpers:
    def setup_method(self):
        self.si = SystemInfo()

    def test_format_bytes(self):
        assert self.si._format_bytes(500) == "500.0 B"
        assert self.si._format_bytes(2048) == "2.0 KB"
        assert self.si._format_bytes(5 * 1024 * 1024) == "5.0 MB"
        assert self.si._format_bytes(3 * 1024**3) == "3.0 GB"
        assert self.si._format_bytes(2 * 1024**4) == "2.0 TB"
        assert self.si._format_bytes(7 * 1024**5) == "7.0 PB"

    def test_get_ram_type(self):
        assert self.si._get_ram_type(20) == "DDR"
        assert self.si._get_ram_type(21) == "DDR2"
        assert self.si._get_ram_type(24) == "DDR3"
        assert self.si._get_ram_type(26) == "DDR4"
        assert self.si._get_ram_type(34) == "DDR5"
        assert self.si._get_ram_type(0) == "Unknown"
        assert self.si._get_ram_type(99) == "Type 99"

    def test_get_wmi_returns_string(self):
        val = self.si._get_wmi("Win32_OperatingSystem", "InstallDate")
        assert val is not None


class TestGetOsInfo:
    def setup_method(self):
        self.si = SystemInfo()

    @patch("app.utils.system_info.platform.uname")
    def test_returns_os_info(self, mock_uname):
        mock_uname.return_value.system = "Windows"
        mock_uname.return_value.release = "10"
        mock_uname.return_value.version = "10.0.19045"
        mock_uname.return_value.machine = "AMD64"
        mock_uname.return_value.node = "PC-01"
        with patch("app.utils.system_info.os.environ.get", return_value="TestUser"):
            info = self.si.get_os_info()
            assert info["name"] == "Windows 10"
            assert info["architecture"] == "AMD64"
            assert info["username"] == "TestUser"
            assert info["computername"] == "PC-01"


class TestGetCpuInfo:
    def setup_method(self):
        self.si = SystemInfo()

    def test_returns_dict(self):
        info = self.si.get_cpu_info()
        assert isinstance(info, dict)


class TestGetRamInfo:
    def setup_method(self):
        self.si = SystemInfo()

    def test_returns_dict(self):
        info = self.si.get_ram_info()
        assert isinstance(info, dict)
        assert "total" in info


class TestGetGpuInfo:
    def setup_method(self):
        self.si = SystemInfo()

    def test_returns_list(self):
        assert isinstance(self.si.get_gpu_info(), list)


class TestGetNetworkInfo:
    def setup_method(self):
        self.si = SystemInfo()

    def test_returns_list(self):
        assert isinstance(self.si.get_network_info(), list)


class TestGetBatteryInfo:
    def setup_method(self):
        self.si = SystemInfo()

    def test_returns_dict_or_none(self):
        result = self.si.get_battery_info()
        assert result is None or isinstance(result, dict)


class TestGetMotherboardInfo:
    def setup_method(self):
        self.si = SystemInfo()

    def test_returns_dict(self):
        info = self.si.get_motherboard_info()
        assert isinstance(info, dict)


class TestGetDrivesInfo:
    def setup_method(self):
        self.si = SystemInfo()

    def test_returns_list(self):
        assert isinstance(self.si.get_drives_info(), list)


class TestGetAll:
    def setup_method(self):
        self.si = SystemInfo()

    @patch("app.utils.system_info.SystemInfo.get_os_info", return_value={"name": "Win"})
    @patch("app.utils.system_info.SystemInfo.get_cpu_info", return_value={"name": "CPU"})
    @patch("app.utils.system_info.SystemInfo.get_ram_info", return_value={"total": "8.0 GB"})
    @patch("app.utils.system_info.SystemInfo.get_gpu_info", return_value=[])
    @patch("app.utils.system_info.SystemInfo.get_motherboard_info", return_value={})
    @patch("app.utils.system_info.SystemInfo.get_drives_info", return_value=[])
    @patch("app.utils.system_info.SystemInfo.get_network_info", return_value=[])
    @patch("app.utils.system_info.SystemInfo.get_battery_info", return_value={})
    def test_get_all_returns_dict(
        self, bat, net, drv, mb, gpu, ram, cpu, osi
    ):
        all_info = self.si.get_all()
        assert "os" in all_info
        assert "cpu" in all_info
        assert "ram" in all_info
        assert "gpu" in all_info
        assert "drives" in all_info
        assert "network" in all_info
        assert "motherboard" in all_info
