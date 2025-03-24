from uvolution.ulogger import LoggerConfig, LoggerLevels, Logger
from uvolution.ulogger.handlers import FileHandler, FormattingHandler

config = LoggerConfig([LoggerLevels.DEBUG, LoggerLevels.INFO,
                       LoggerLevels.WARNING, LoggerLevels.ERROR, LoggerLevels.CRITICAL])

config.add_handler(FormattingHandler())
config.add_handler(FileHandler('uvolution.log', 'w'))

logger = Logger(config)


def main():
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
    logger.close()


if __name__ == "__main__":
    main()
