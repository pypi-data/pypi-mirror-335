from binance_data_processor import launch_data_listener


class SampleObserverClass:
    @staticmethod
    def update(message):
        print(f"message: {message}")

if __name__ == '__main__':
    from setuptools import setup, find_packages

    print(find_packages())

    sample_observer = SampleObserverClass()

    data_listener = launch_data_listener(observers=[sample_observer])
