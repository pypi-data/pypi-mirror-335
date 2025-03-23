import platform
from locale import getencoding
from pathlib import Path
from typing import Union

import psutil
from pendulum import DateTime, Interval, from_timestamp, local_timezone, now
from PySide6.QtCore import QLocale, QObject, QSysInfo, QUrl
from PySide6.QtGui import QDesktopServices


class OS(QObject):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def name() -> str:
        return platform.system()

    @staticmethod
    def boot_unique_id() -> str:
        return QSysInfo.bootUniqueId().toStdString()

    @staticmethod
    def build_abi() -> str:
        return QSysInfo.buildAbi()

    @staticmethod
    def build_cpu_architecture() -> str:
        return QSysInfo.buildCpuArchitecture()

    @staticmethod
    def current_cpu_architecture() -> str:
        return QSysInfo.currentCpuArchitecture()

    @staticmethod
    def kernel_type() -> str:
        return QSysInfo.kernelType()

    @staticmethod
    def kernel_version() -> str:
        return QSysInfo.kernelVersion()

    @staticmethod
    def machine_host_name() -> str:
        return QSysInfo.machineHostName()

    @staticmethod
    def machine_unique_id() -> str:
        return QSysInfo.machineUniqueId().toStdString()

    @staticmethod
    def pretty_product_name() -> str:
        return QSysInfo.prettyProductName()

    @staticmethod
    def product_type() -> str:
        return QSysInfo.productType()

    @staticmethod
    def product_version() -> str:
        return QSysInfo.productVersion()

    @staticmethod
    def boot_time() -> DateTime:
        return from_timestamp(psutil.boot_time(), local_timezone().name)

    @staticmethod
    def up_time() -> Interval:
        return now().diff(OS.boot_time())

    @staticmethod
    def timezone() -> str:
        return local_timezone().name

    @staticmethod
    def locale() -> str:
        return QLocale.system().name(QLocale.TagSeparator.Underscore)

    @staticmethod
    def encoding() -> str:
        return getencoding()

    @staticmethod
    def open_url(url: Union[QUrl, str]) -> bool:
        return QDesktopServices.openUrl(url)

    @staticmethod
    def open_path(path: Union[Path, str]) -> bool:
        if isinstance(path, str):
            path = Path(path)

        return QDesktopServices.openUrl(path.resolve().as_uri())
