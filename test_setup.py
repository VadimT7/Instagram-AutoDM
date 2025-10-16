"""
Test script to verify installation and setup
"""
import sys
import os
from colorama import init, Fore, Style

init(autoreset=True)

def test_imports():
    """Test if all required packages are installed"""
    print(f"{Fore.CYAN}Testing package imports...{Style.RESET_ALL}")
    
    packages = [
        ('selenium', 'Selenium WebDriver'),
        ('undetected_chromedriver', 'Undetected ChromeDriver'),
        ('pandas', 'Pandas'),
        ('dotenv', 'Python-dotenv'),
        ('colorama', 'Colorama'),
        ('numpy', 'NumPy'),
        ('pyautogui', 'PyAutoGUI'),
        ('fake_useragent', 'Fake UserAgent')
    ]
    
    all_good = True
    for package, name in packages:
        try:
            __import__(package)
            print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {name} installed")
        except ImportError:
            print(f"{Fore.RED}[X]{Style.RESET_ALL} {name} not installed")
            all_good = False
    
    return all_good

def test_files():
    """Test if required files exist"""
    print(f"\n{Fore.CYAN}Testing required files...{Style.RESET_ALL}")
    
    files = [
        ('InstagramProfiles.csv', 'CSV input file'),
        ('config.py', 'Configuration file'),
        ('main.py', 'Main script'),
        ('browser_manager.py', 'Browser manager'),
        ('instagram_automation.py', 'Instagram automation'),
        ('human_behavior.py', 'Human behavior module'),
        ('csv_processor.py', 'CSV processor')
    ]
    
    all_good = True
    for file, description in files:
        if os.path.exists(file):
            print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {description} found")
        else:
            print(f"{Fore.RED}[X]{Style.RESET_ALL} {description} not found")
            all_good = False
    
    # Check for .env file
    if os.path.exists('.env'):
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} .env file found")
    else:
        print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} .env file not found (create from env.example)")
    
    return all_good

def test_chrome():
    """Test if Chrome browser is available"""
    print(f"\n{Fore.CYAN}Testing Chrome browser...{Style.RESET_ALL}")
    
    try:
        import undetected_chromedriver as uc
        from selenium import webdriver
        
        print("Attempting to create Chrome driver...")
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        driver.quit()
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Chrome browser working")
        return True
    except Exception as e:
        print(f"{Fore.RED}[X]{Style.RESET_ALL} Chrome browser error: {e}")
        print(f"{Fore.YELLOW}Make sure Chrome browser is installed{Style.RESET_ALL}")
        return False

def main():
    """Run all tests"""
    print(f"""
{Fore.CYAN}===============================================
   Instagram DM Automation Test Suite
==============================================={Style.RESET_ALL}
    """)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test files
    files_ok = test_files()
    
    # Test Chrome
    chrome_ok = test_chrome()
    
    # Summary
    print(f"\n{Fore.CYAN}=============== Summary ==============={Style.RESET_ALL}")
    
    if imports_ok and files_ok and chrome_ok:
        print(f"{Fore.GREEN}[OK] All tests passed! The system is ready to use.{Style.RESET_ALL}")
        print(f"\nNext steps:")
        print(f"1. Create .env file from env.example and add your Instagram credentials")
        print(f"2. Add Instagram usernames to InstagramProfiles.csv")
        print(f"3. Run: python main.py")
        return 0
    else:
        print(f"{Fore.RED}[X] Some tests failed. Please fix the issues above.{Style.RESET_ALL}")
        
        if not imports_ok:
            print(f"\n{Fore.YELLOW}To install missing packages, run:{Style.RESET_ALL}")
            print(f"pip install -r requirements.txt")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
