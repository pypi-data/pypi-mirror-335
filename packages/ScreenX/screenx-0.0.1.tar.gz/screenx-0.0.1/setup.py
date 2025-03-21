from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    # name="ScrapeX",
    name="ScreenX",
    version="0.0.1",
    description='''The Ultimate AI-Powered Web Automation & Scraping Bot
    ScreenX is a next-generation Python package designed to automate web interactions, intelligently navigate websites, and extract valuable data—all with minimal effort. Whether you're looking to automate repetitive web tasks, interact with dynamic content, or scrape large datasets, ScreenX provides a seamless and efficient solution.

    Powered by Selenium, BeautifulSoup, and AI-driven decision-making, ScreenX can mimic human-like browsing behavior, fill forms, click buttons, handle pop-ups, and even bypass anti-bot mechanisms. It supports headless browsing for efficiency, multi-threading for high-speed scraping, and CAPTCHA-solving integration for uninterrupted automation.

    With an intuitive API, ScreenX allows users to define actions dynamically, making it perfect for automated research, e-commerce monitoring, social media engagement, and competitor analysis. Whether you need real-time data extraction or full-scale website interaction, ScreenX is your go-to automation toolkit.

    Designed for developers, businesses, and researchers alike, ScreenX eliminates the complexity of web automation—letting you focus on results, not code. 🚀

    ✅ Key Features:
    ✔️ Intelligent Web Navigation & Automation
    ✔️ Advanced Web Scraping with Dynamic Handling
    ✔️ AI-Powered Decision Making & Interaction
    ✔️ Headless Browsing for High Performance
    ✔️ Anti-Bot Detection Evasion & CAPTCHA Handling
    ✔️ Multi-Threaded Scraping for Faster Execution
    ✔️ Easy-to-Use API for Seamless Integration

    Say goodbye to manual web interactions—ScreenX does it all for you! 🕵️‍♂️💻''',
    package_dir={"": "ScreenX"},
    packages=find_packages(where='ScreenX'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/ArjanCodes/2023-package",
    author="Hitarth B",
    author_email="structureddatadrive@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=["selenium >= 4.24.0","pandas>=2.2.2"],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.6",
)