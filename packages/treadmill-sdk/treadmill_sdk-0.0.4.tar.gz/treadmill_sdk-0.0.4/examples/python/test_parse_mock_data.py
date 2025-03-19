"""
Treadmill SDK Demo
演示使用 treadmill_sdk 库解析模拟数据。
"""

from typing import Final
import treadmill_sdk
import logging
from logger import getLogger

# 配置日志记录器
logger = getLogger(logging.INFO)

# 42 52 4E 43 02 13 1E 00 03 01 A5 5A ED A9 F1 8A E0 15 7C 0A FF E5 F3 3D 7F 59 28 BE 6C 53 7D EE 0C 40 94 B7 E6 72 26 56 D5 C4 9E
# 42 52 4E 43 02 13 1F 00 03 01 A5 5A EC A9 E5 8A C0 B9 65 13 D6 25 1C 6A 2E 88 D7 B0 4F 5D 52 E9 E6 0D 4B 47 07 1B 0F DF 2A DC AC 73

# 定义常量
MOCK_DATA: Final[bytes] = bytes.fromhex(
    "42524E4302131E000301A55AEDA9F18AE0157C0AFFE5F33D7F5928BE6C537DEE0C4094B7E6722656D5C49E"
    "42524E4302131F000301A55AEC A9E58AC0B96513D6251C6A2E88D7B04F5D52E9E60D4B47071B0FDF2ADCAC73"
)


class TreadmillDataParser:
    """跑步机数据解析器"""

    def __init__(self) -> None:
        """初始化解析器并设置回调"""
        self._setup_callbacks()

    def _setup_callbacks(self) -> None:
        """设置回调函数"""
        treadmill_sdk.set_abnormal_event_callback(self._on_abnormal_event)
        treadmill_sdk.set_gait_data_callback(self._on_gait_data)

    def _on_abnormal_event(self, timestamp: int, event: int) -> None:
        """异常事件回调处理"""
        logger.info(
            f"检测到异常事件:" f"\n  - timstamp: {timestamp}" f"\n  - 事件类型: {event}"
        )

    def _on_gait_data(
        self, timestamp: int, left_foot: bool, pattern: int, gait_duration: int
    ) -> None:
        """步态数据回调处理"""
        logger.info(
            f"收到步态数据:"
            f"\n  - timstamp: {timestamp}"
            f"\n  - 左脚: {left_foot}"
            f"\n  - 模式: {pattern}"
            f"\n  - duration: {gait_duration}ms"
        )

    def parse_data(self, data: bytes) -> None:
        """解析数据"""
        try:
            logger.info(f"开始解析数据: 长度={len(data)}字节")
            logger.debug(f"原始数据(hex): {data.hex()}")

            treadmill_sdk.did_receive_data(data)

        except Exception as e:
            logger.error(f"数据解析失败: {e}")
            raise


def main() -> None:
    """主函数"""
    try:
        parser = TreadmillDataParser()
        parser.parse_data(MOCK_DATA)

    except KeyboardInterrupt:
        logger.info("程序被用户终止")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        raise


if __name__ == "__main__":
    main()
