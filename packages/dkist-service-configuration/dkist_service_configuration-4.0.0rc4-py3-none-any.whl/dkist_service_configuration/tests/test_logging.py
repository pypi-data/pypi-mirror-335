"""Tests for the logging module"""
import logging

from dkist_service_configuration.logging import logger

std_logger = logging.getLogger(__name__)


def test_log_levels():
    logger.trace("trace")
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")


def test_log_levels_std_logger():
    std_logger.debug("debug")
    std_logger.info("info")
    std_logger.warning("warning")
    std_logger.error("error")
