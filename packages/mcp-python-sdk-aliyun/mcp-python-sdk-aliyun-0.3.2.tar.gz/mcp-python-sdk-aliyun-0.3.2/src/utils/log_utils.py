import logging


def init_logger(log_file):
    try:
        # 创建logger对象
        logger = logging.getLogger('my_logger')
        logger.setLevel(logging.DEBUG)  # 设置最低的日志级别

        # 创建一个文件处理器，并将日志输出到指定文件
        file_handler = logging.FileHandler(log_file)
        # 设置文件处理器的日志级别
        file_handler.setLevel(logging.DEBUG)
        # 创建一个日志格式器并将其添加到处理器
        formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
        file_handler.setFormatter(formatter)
        # 将处理器添加到logger对象中
        logger.addHandler(file_handler)
        return logger
    except Exception as e:
        return None


def log_info(logger, text):
    if logger:
        logger.info(text)


def log_error(logger, text):
    if logger:
        logger.error(text)

