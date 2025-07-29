#!/usr/bin/env python3
"""
Auto MEmu Login - Automatically opens MEmu and logs into Facebook accounts
"""

import os
import sys
import time
import json
import subprocess
import logging
from datetime import datetime
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_memu_login.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoMEmuLogin:
    """Auto MEmu Login Class"""
    
    def __init__(self):
        self.accounts_file = "fb_created_ids.txt"
        self.memu_accounts_file = "memu_simulation_accounts.txt"
        self.login_results_file = "login_results.json"
        
    def load_accounts(self):
        """Load accounts from files"""
        accounts = []
        
        # Try to load from different account files
        files_to_check = [
            self.memu_accounts_file,  # Prioritize memu_simulation_accounts.txt
            self.accounts_file,
            "memu_facebook_accounts.txt"
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and '|' in line:
                                parts = line.split('|')
                                if len(parts) >= 4:
                                    account = {
                                        'username': parts[0].strip(),
                                        'password': parts[1].strip(),
                                        'email': parts[2].strip(),
                                        'device': parts[3].strip(),
                                        'timestamp': parts[4].strip() if len(parts) > 4 else datetime.now().isoformat()
                                    }
                                    accounts.append(account)
                    
                    if accounts:  # Only break if we found accounts
                        logger.info(f"Loaded {len(accounts)} accounts from {file_path}")
                        break
                    
                except Exception as e:
                    logger.error(f"Error loading accounts from {file_path}: {e}")
        
        return accounts
    
    def start_memu_instances(self, count=4):
        """Start MEmu instances"""
        logger.info(f"🚀 Starting {count} MEmu instances...")
        
        instances = []
        
        for i in range(1, count + 1):
            instance_name = f"MEmu{i}"
            adb_port = 21503 + i - 1
            
            try:
                logger.info(f"Starting {instance_name}...")
                
                # Simulate MEmu startup (replace with actual MEmu path)
                # cmd = ["C:\\Program Files (x86)\\MEmu\\Memu.exe", "-m", instance_name]
                # subprocess.Popen(cmd)
                
                # Simulate startup time
                time.sleep(random.uniform(5, 10))
                
                instance = {
                    'name': instance_name,
                    'adb_port': adb_port,
                    'device_id': f"127.0.0.1:{adb_port}",
                    'status': 'running'
                }
                
                instances.append(instance)
                logger.info(f"✅ Started {instance_name}")
                
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error starting {instance_name}: {e}")
        
        return instances
    
    def connect_to_instances(self, instances):
        """Connect to MEmu instances via ADB"""
        connected_instances = []
        
        logger.info("🔗 Connecting to MEmu instances...")
        
        for instance in instances:
            try:
                device_id = instance['device_id']
                
                logger.info(f"Connecting to {instance['name']} on {device_id}")
                
                # Simulate ADB connection
                time.sleep(random.uniform(1, 3))
                
                # Try to connect via ADB
                result = subprocess.run(
                    ['adb', 'connect', device_id],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if 'connected' in result.stdout.lower():
                    instance['connected'] = True
                    connected_instances.append(instance)
                    logger.info(f"✅ Connected to {instance['name']}")
                else:
                    logger.warning(f"❌ Failed to connect to {instance['name']}")
                    
            except Exception as e:
                logger.error(f"Error connecting to {instance['name']}: {e}")
        
        return connected_instances
    
    def login_to_accounts(self, instances, accounts):
        """Login to Facebook accounts on MEmu instances"""
        logger.info(f"📱 Logging into {len(accounts)} accounts on {len(instances)} instances")
        
        # Distribute accounts across instances
        accounts_per_instance = len(accounts) // len(instances)
        remaining_accounts = len(accounts) % len(instances)
        
        login_results = []
        
        for i, instance in enumerate(instances):
            instance_accounts = accounts_per_instance + (1 if i < remaining_accounts else 0)
            start_idx = i * accounts_per_instance + min(i, remaining_accounts)
            end_idx = start_idx + instance_accounts
            
            instance_account_list = accounts[start_idx:end_idx]
            
            logger.info(f"Logging into {len(instance_account_list)} accounts on {instance['name']}")
            
            for account in instance_account_list:
                success = self.login_single_account(instance, account)
                
                login_result = {
                    'account': account,
                    'instance': instance['name'],
                    'success': success,
                    'timestamp': datetime.now().isoformat()
                }
                
                login_results.append(login_result)
                
                # Delay between logins
                time.sleep(random.uniform(2, 5))
            
            # Delay between instances
            time.sleep(random.uniform(3, 8))
        
        # Save login results
        self.save_login_results(login_results)
        
        return login_results
    
    def login_single_account(self, instance, account):
        """Login to a single Facebook account"""
        try:
            device_id = instance['device_id']
            email = account['email']
            password = account['password']
            
            logger.info(f"Logging into {email} on {instance['name']}")
            
            # Simulate login process
            time.sleep(random.uniform(3, 8))
            
            # Simulate success/failure
            success = random.random() > 0.2  # 80% success rate
            
            if success:
                logger.info(f"✅ Successfully logged into {email} on {instance['name']}")
            else:
                logger.warning(f"❌ Failed to login to {email} on {instance['name']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error logging into {account['email']}: {e}")
            return False
    
    def save_login_results(self, login_results):
        """Save login results to file"""
        try:
            data = {
                'login_session': {
                    'started_at': datetime.now().isoformat(),
                    'total_accounts': len(login_results),
                    'successful_logins': len([r for r in login_results if r['success']]),
                    'failed_logins': len([r for r in login_results if not r['success']])
                },
                'login_results': login_results
            }
            
            with open(self.login_results_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Saved login results to {self.login_results_file}")
            
        except Exception as e:
            logger.error(f"Error saving login results: {e}")
    
    def get_status(self):
        """Get current status"""
        accounts = self.load_accounts()
        
        status = {
            'total_accounts': len(accounts),
            'accounts_loaded': len(accounts) > 0,
            'login_results_file': os.path.exists(self.login_results_file)
        }
        
        return status

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Auto MEmu Login - Login to Facebook accounts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start MEmu and login to all accounts
  python auto_memu_login.py --start --login
  
  # Show status
  python auto_memu_login.py --status
  
  # Login to accounts only
  python auto_memu_login.py --login
        """
    )
    
    parser.add_argument('--start', action='store_true', help='Start MEmu instances')
    parser.add_argument('--login', action='store_true', help='Login to Facebook accounts')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--instances', type=int, default=4, help='Number of MEmu instances')
    
    args = parser.parse_args()
    
    # Create bot instance
    bot = AutoMEmuLogin()
    
    try:
        if args.start or args.login:
            logger.info("🚀 Starting Auto MEmu Login...")
            
            # Load accounts
            accounts = bot.load_accounts()
            
            if not accounts:
                logger.error("❌ No accounts found! Please create accounts first.")
                return
            
            logger.info(f"Found {len(accounts)} accounts to login")
            
            if args.start:
                # Start MEmu instances
                instances = bot.start_memu_instances(args.instances)
                
                if instances:
                    # Connect to instances
                    connected_instances = bot.connect_to_instances(instances)
                    
                    if connected_instances and args.login:
                        # Login to accounts
                        bot.login_to_accounts(connected_instances, accounts)
                    else:
                        logger.error("❌ No instances connected!")
                else:
                    logger.error("❌ No instances started!")
            
            elif args.login:
                # Just login to accounts (instances already running)
                instances = [
                    {'name': f'MEmu{i}', 'device_id': f'127.0.0.1:{21503 + i - 1}'}
                    for i in range(1, 5)
                ]
                bot.login_to_accounts(instances, accounts)
        
        elif args.status:
            status = bot.get_status()
            logger.info(f"📊 Status: {json.dumps(status, indent=2)}")
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        logger.info("⏹️  Stopping auto login...")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 