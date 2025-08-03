#!/usr/bin/env python3
from services.config_service import config

print('Testing config loading...')
try:
    instances = config.get_target_instances()
    print(f'✅ Config loaded successfully')
    print(f'📊 Target instances: {len(instances)}')
    
    for i, instance in enumerate(instances):
        print(f'  {i+1}. {instance.get("name")}: {instance.get("url")}')
        print(f'     Auth: {instance.get("auth", {}).get("type")}')
    
    # Test API config
    api_config = config.get_api_config()
    print(f'🌐 API base URL: {api_config.get("base_url")}')
    
except Exception as e:
    print(f'❌ Config loading failed: {e}')
    import traceback
    traceback.print_exc()